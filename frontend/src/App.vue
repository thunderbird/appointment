<script setup lang="ts">
import { createFetch } from '@vueuse/core';
import {
  inject, provide, computed, onMounted,
} from 'vue';
import { useRoute, useRouter } from 'vue-router';
import NavBar from '@/components/NavBar.vue';
import TitleBar from '@/components/TitleBar.vue';
import FooterBar from '@/components/FooterBar.vue';
import SiteNotification from '@/elements/SiteNotification.vue';
import { useSiteNotificationStore } from '@/stores/alert-store';
import { storeToRefs } from 'pinia';
import { getPreferredTheme } from '@/utils';

// stores
import { useUserStore } from '@/stores/user-store';
import { useCalendarStore } from '@/stores/calendar-store';
import { useAppointmentStore } from '@/stores/appointment-store';
import { useScheduleStore } from '@/stores/schedule-store';
import RouteNotFoundView from '@/views/errors/RouteNotFoundView.vue';
import NotAuthenticatedView from '@/views/errors/NotAuthenticatedView.vue';
import UAParser from 'ua-parser-js';
import posthog from 'posthog-js';
import {
  apiUrlKey, callKey, refreshKey, isPasswordAuthKey, isFxaAuthKey, fxaEditProfileUrlKey, usePosthogKey,
} from '@/keys';
import { StringResponse } from '@/models';

// component constants
const currentUser = useUserStore(); // data: { username, email, name, level, timezone, id }
const apiUrl = inject(apiUrlKey);
const route = useRoute();
const routeName = typeof route.name === 'string' ? route.name : '';
const router = useRouter();
const siteNotificationStore = useSiteNotificationStore();
const {
  isVisible: visibleNotification,
  title: notificationTitle,
  actionUrl: notificationActionUrl,
  message: notificationMessage,
} = storeToRefs(siteNotificationStore);

const {
  isSame: isSameNotification,
  show: showNotification,
  lock: lockNotification,
} = siteNotificationStore;

// handle auth and fetch
const isAuthenticated = computed(() => currentUser?.exists());
const call = createFetch({
  baseUrl: apiUrl,
  options: {
    beforeFetch({ options }) {
      if (isAuthenticated.value) {
        const token = currentUser.data.accessToken;
        // @ts-ignore
        options.headers.Authorization = `Bearer ${token}`;
      }
      return { options };
    },
    updateDataOnError: true, // Needed to access the actual error message...
    async onFetchError(context) {
      const { data, response } = context;
      // Catch any google refresh error that may occur
      if (
        data?.detail?.id === 'GOOGLE_REFRESH_ERROR'
        && !isSameNotification('GOOGLE_REFRESH_ERROR')
      ) {
        // Ensure other async calls don't reach here
        lockNotification(data.detail.error);

        // Retrieve the google auth url, and if that fails send them to calendar settings!
        const { data: urlData, error: urlError }: StringResponse = await call('google/auth').get();
        const url = urlError.value ? '/settings/calendar' : (urlData.value as string).slice(1, -1);

        // Update our site notification store with the error details
        showNotification(
          data.detail.error,
          'Action needed!',
          data.detail?.message || 'Please re-connect with Google',
          url,
        );
      } else if (response && response.status === 401 && data?.detail?.id === 'INVALID_TOKEN') {
        // Clear current user data, and ship them to the login screen!
        currentUser.$reset();
        await router.push('/login');
        return context;
      }

      // Pass the error along
      return context;
    },
  },
  fetchOptions: {
    mode: 'cors',
    credentials: 'include',
  },
});

// TODO: Deprecated - Please use callKey, as it's typed!
provide('call', call);
provide(callKey, call);

// TODO: Deprecated - Please use isPasswordAuthKey, as it's typed!
provide('isPasswordAuth', import.meta.env?.VITE_AUTH_SCHEME === 'password');
provide(isPasswordAuthKey, import.meta.env?.VITE_AUTH_SCHEME === 'password');
// TODO: Deprecated - Please use isFxaAuthKey, as it's typed!
provide('isFxaAuth', import.meta.env?.VITE_AUTH_SCHEME === 'fxa');
provide(isFxaAuthKey, import.meta.env?.VITE_AUTH_SCHEME === 'fxa');
// TODO: Deprecated - Please use fxaEditProfileUrlKey, as it's typed!
provide('fxaEditProfileUrl', import.meta.env?.VITE_FXA_EDIT_PROFILE);
provide(fxaEditProfileUrlKey, import.meta.env?.VITE_FXA_EDIT_PROFILE);

// menu items for main navigation
const navItems = [
  'calendar',
  'schedule',
  'bookings',
  'settings',
];

// db tables
const calendarStore = useCalendarStore();
const appointmentStore = useAppointmentStore();
const scheduleStore = useScheduleStore();
const userStore = useUserStore();

// true if route can be accessed without authentication
const routeIsPublic = computed(
  () => route.meta?.isPublic,
);
const routeIsHome = computed(
  () => ['home'].includes(routeName),
);
const routeHasModal = computed(
  () => ['login'].includes(routeName),
);

// retrieve calendars and appointments after checking login and persisting user to db
const getDbData = async () => {
  if (currentUser?.exists()) {
    await Promise.all([
      userStore.profile(call),
      calendarStore.fetch(call),
      appointmentStore.fetch(call),
      scheduleStore.fetch(call),
    ]);
  }
};

const onPageLoad = async () => {
  /**
   * Metric collection for development purposes.
   * This data will be used to help guide development, design, and user experience decisions.
   */
  const parser = new UAParser(navigator.userAgent);
  const browser = parser.getBrowser();
  const os = parser.getOS();
  const device = parser.getDevice();
  const deviceRes = `${window?.screen?.width ?? -1}x${window?.screen?.height ?? -1}`;
  const effectiveDeviceRes = `${window?.screen?.availWidth ?? -1}x${window?.screen?.availHeight ?? -1}`;

  const response = await call('metrics/page-load').post({
    browser: browser.name,
    browser_version: `${browser.name}:${browser.version}`,
    os: os.name,
    os_version: `${os.name}:${os.version}`,
    device: device.model,
    device_model: `${device.vendor}:${device.model}`,
    resolution: deviceRes,
    effective_resolution: effectiveDeviceRes,
    user_agent: navigator.userAgent,
    locale: localStorage?.getItem('locale') ?? navigator.language,
    theme: getPreferredTheme(),
  }).json();

  const { data } = response;
  return data.value?.id ?? false;
};

// TODO: Deprecated - Please use refreshKey, as it's typed!
provide('refresh', getDbData);
// provide refresh functions for components
provide(refreshKey, getDbData);

onMounted(async () => {
  const usePosthog = inject(usePosthogKey);

  if (usePosthog) {
    posthog.init(import.meta.env.VITE_POSTHOG_PROJECT_KEY, {
      api_host: import.meta.env.VITE_POSTHOG_HOST,
      person_profiles: 'identified_only',
      persistence: 'memory',
      mask_all_text: true,
      mask_all_element_attributes: true,
      sanitize_properties: (properties, event) => {
        // If the route isn't available to use right now, ignore the capture.
        if (!route.name) {
          return {};
        }

        // Do we need to mask the path?
        if (route.meta?.maskForMetrics) {
          // Replace recorded path with the path definition
          const vuePath = route.matched[0]?.path ?? '<unknown path to mask>';
          const oldPath = properties.$pathname;
          const oldUrl = properties.$current_url;

          properties.$pathname = vuePath;
          properties.$current_url = properties.$current_url.replace(oldPath, vuePath);

          // Also if this is the first capture, ensure we cover their initial url
          if (properties.$initial_person_info?.u === oldUrl) {
            properties.$initial_person_info.u = properties.$current_url;
          }
        }

        if (event === '$pageleave') {
          // We don't have access to the previous route, so just null it out.
          properties.$prev_pageview_pathname = null;
        }

        return properties;
      },
    });
    posthog.register({
      service: 'apmt',
    });

    const id = await onPageLoad();

    if (isAuthenticated.value) {
      const profile = useUserStore();
      posthog.identify(profile.data.uniqueHash);
    } else if (id) {
      posthog.identify(id);
    }
  }
});

</script>

<template>
  <!-- authenticated subscriber content -->
  <template v-if="router.hasRoute(route.name) && (isAuthenticated || routeIsPublic)">
    <site-notification
      v-if="isAuthenticated && visibleNotification"
      :title="notificationTitle"
      :action-url="notificationActionUrl"
    >
      {{ notificationMessage }}
    </site-notification>
    <nav-bar v-if="isAuthenticated" :nav-items="navItems"/>
    <title-bar v-if="routeIsPublic"/>
    <main
      :class="{
        'mx-4 min-h-full py-32 lg:mx-8': !routeIsHome && !routeIsPublic,
        '!pt-24': routeIsHome || isAuthenticated,
        'min-h-full pb-32 pt-8': routeIsPublic && !routeHasModal,
      }"
    >
      <router-view/>
    </main>
    <footer-bar/>
  </template>
  <template v-else-if="router.hasRoute(route.name) && !routeIsPublic">
    <not-authenticated-view/>
  </template>
  <template v-else>
    <route-not-found-view/>
  </template>
</template>
