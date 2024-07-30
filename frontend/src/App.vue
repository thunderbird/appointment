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

<script setup>
import { createFetch } from '@vueuse/core';
import {
  inject, provide, computed, onMounted,
} from 'vue';
import { useRoute, useRouter } from 'vue-router';
import NavBar from '@/components/NavBar';
import TitleBar from '@/components/TitleBar';
import FooterBar from '@/components/FooterBar.vue';
import SiteNotification from '@/elements/SiteNotification';
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
import { callKey, refreshKey, usePosthogKey } from '@/keys';
import UAParser from 'ua-parser-js';
import posthog from 'posthog-js';

// component constants
const currentUser = useUserStore(); // data: { username, email, name, level, timezone, id }
const apiUrl = inject('apiUrl');
const route = useRoute();
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
    async beforeFetch({ options }) {
      if (isAuthenticated.value) {
        const token = await currentUser.data.accessToken;
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
        const { data: urlData, error: urlError } = await call('google/auth').get();
        const url = urlError.value ? '/settings/calendar' : urlData.value.slice(1, -1);

        // Update our site notification store with the error details
        showNotification(
          data.detail.error,
          'Action needed!',
          data.detail?.message || 'Please re-connect with Google',
          url,
        );
      } else if (response && response.status === 401 && data?.detail?.id === 'INVALID_TOKEN') {
        // Clear current user data, and ship them to the login screen!
        await currentUser.$reset();
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

// Deprecated - Please use callKey, as it's typed!
provide('call', call);
provide(callKey, call);

provide('isPasswordAuth', import.meta.env?.VITE_AUTH_SCHEME === 'password');
provide('isFxaAuth', import.meta.env?.VITE_AUTH_SCHEME === 'fxa');
provide('fxaEditProfileUrl', import.meta.env?.VITE_FXA_EDIT_PROFILE);

// menu items for main navigation
const navItems = [
  'calendar',
  'schedule',
  'appointments',
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
  () => ['home'].includes(route.name),
);
const routeHasModal = computed(
  () => ['login'].includes(route.name),
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

// Deprecated - Please use refreshKey, as it's typed!
provide('refresh', getDbData);
// provide refresh functions for components
provide(refreshKey, getDbData);

onMounted(async () => {
  const usePosthog = inject(usePosthogKey);
  const id = await onPageLoad();

  if (usePosthog && isAuthenticated.value) {
    const profile = useUserStore();
    posthog.identify(profile.data.uniqueHash);
  } else if (usePosthog && id) {
    posthog.identify(id);
  }
});

</script>
