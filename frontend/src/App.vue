<script setup lang="ts">
import { createFetch } from '@vueuse/core';
import {
  inject, provide, computed, onMounted,
} from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import UAParser from 'ua-parser-js';
import NavBar from '@/components/NavBar.vue';
import TitleBar from '@/components/TitleBar.vue';
import FooterBar from '@/components/FooterBar.vue';
import SiteNotification from '@/elements/SiteNotification.vue';
import RouteNotFoundView from '@/views/errors/RouteNotFoundView.vue';
import NotAuthenticatedView from '@/views/errors/NotAuthenticatedView.vue';
import {
  apiUrlKey,
  callKey,
  refreshKey,
  isPasswordAuthKey,
  isFxaAuthKey,
  fxaEditProfileUrlKey,
  isAccountsAuthKey,
} from '@/keys';
import { StringResponse } from '@/models';
import { usePosthog, posthog } from '@/composables/posthog';

// stores
import { useSiteNotificationStore } from '@/stores/alert-store';
import { useUserStore } from '@/stores/user-store';
import { createCalendarStore } from '@/stores/calendar-store';
import { createAppointmentStore } from '@/stores/appointment-store';
import { createScheduleStore } from '@/stores/schedule-store';
import { AuthSchemes } from '@/definitions';

// component constants
const user = useUserStore();
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

const isAccountsAuth = () => import.meta.env?.VITE_AUTH_SCHEME === AuthSchemes.Accounts;

provide(isPasswordAuthKey, import.meta.env?.VITE_AUTH_SCHEME === AuthSchemes.Password);
provide(isFxaAuthKey, import.meta.env?.VITE_AUTH_SCHEME === AuthSchemes.Fxa);
provide(fxaEditProfileUrlKey, import.meta.env?.VITE_FXA_EDIT_PROFILE);
provide(isAccountsAuthKey, isAccountsAuth());

// handle auth and fetch
const call = createFetch({
  baseUrl: apiUrl,
  options: {
    beforeFetch({ options }) {
      if (isAccountsAuth) {
        // Cookies are somehow still stored as a giant `;` separated string, so do a bunch of array nonsense to retrieve our token
        const csrf = window.document.cookie?.split('; csrftoken=')?.pop()?.split(';')?.shift()
          ?.trim() ?? null;
        // If you change csrf safe_methods parameter, change this too!
        if (!['GET', 'OPTIONS', 'HEAD', 'TRACE'].includes(options?.method ?? 'GET') && csrf) {
          options.headers['X-CSRFToken'] = csrf;
        }
      }

      if (user?.authenticated) {
        const token = user.data.accessToken;
        // @ts-expect-error ignore headers type error
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
        user.$reset();
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

// Now that we created the call function, we can initialize API calls for the user store
user.init(call);

provide(callKey, call);

// menu items for main navigation
const navItems = [
  'dashboard',
  'bookings',
  'settings',
];

// db tables
const calendarStore = createCalendarStore(call);
const appointmentStore = createAppointmentStore(call);
const scheduleStore = createScheduleStore(call);

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
  if (user?.authenticated) {
    await Promise.all([
      user.profile(),
      calendarStore.fetch(),
      appointmentStore.fetch(),
      scheduleStore.fetch(),
    ]);
  }
};

const onPageLoad = async () => {
  /**
   * Metric collection for development purposes.
   * This data will be used to help guide development, design, and user experience decisions.
   */
  /*
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
    locale: defaultLocale(), // needs to import defaultLocale from utils
  }).json();

  const { data } = response;
  return data.value?.id ?? false;
   */

  // Only used for non-subscribers
  const parser = new UAParser(navigator.userAgent);
  const browser = parser.getBrowser();
  const os = parser.getOS();

  const response = await call('metrics/get-id').post({
    browser_version: `${browser.name}:${browser.version}`,
    os_version: `${os.name}:${os.version}`,
  }).json();
  const { data } = response;
  return data.value?.id ?? false;
};

// provide refresh functions for components
provide(refreshKey, getDbData);

onMounted(async () => {
  // Ensure we have a cookie available for POST/PUT/DELETEs
  await call('session-info').get();

  if (usePosthog) {
    const REMOVED_PROPERTY = '<removed>';
    const UNKNOWN_PROPERTY = '<unknown>';

    // Hack to clear $set_once until we get confirmation that this can be filtered.
    // Move the function reference so we can patch it and still retrieve the results before we sanitize it.

    /* eslint no-underscore-dangle: ["error", { "allow": ["_calculate_set_once_properties"] }] */

    if (posthog['_original_calculate_set_once_properties'] === undefined) {
      posthog['_original_calculate_set_once_properties'] = posthog._calculate_set_once_properties;
    }
    posthog._calculate_set_once_properties = function patch(dataSetOnce?) {
      dataSetOnce = posthog['_original_calculate_set_once_properties'](dataSetOnce);

      if (dataSetOnce?.$initial_current_url || dataSetOnce?.$initial_pathname) {
        dataSetOnce.$initial_current_url = REMOVED_PROPERTY;
        dataSetOnce.$initial_pathname = REMOVED_PROPERTY;
      }

      return dataSetOnce;
    };

    posthog.init(import.meta.env.VITE_POSTHOG_PROJECT_KEY, {
      api_host: import.meta.env.VITE_POSTHOG_HOST,
      ui_host: import.meta.env.VITE_POSTHOG_UI_HOST,
      person_profiles: 'identified_only',
      persistence: 'memory',
      mask_all_text: true,
      mask_all_element_attributes: true,
      autocapture: false, // Off for now until we can figure out $set_once.
      sanitize_properties: (properties, event) => {
        // If the route isn't available to use right now, ignore the capture.
        if (!route.name) {
          return {
            captureFailedMessage: 'route.name was not available.',
          };
        }

        // Do we need to mask the path?
        if (route.meta?.maskForMetrics) {
          // Replace recorded path with the path definition
          // So basically: /user/melissaa/dfb0d2aa/ -> /user/:username/:signatureOrSlug
          const vuePath = route.matched[0]?.path ?? UNKNOWN_PROPERTY;
          const oldPath = properties.$pathname;

          // Easiest just to string replace all instances!
          let json = JSON.stringify(properties);
          // replaceAll that typescript won't complain about...
          if (properties?.$current_url) {
            json = json.replace(new RegExp(properties.$current_url, 'gi'), properties.$current_url.replace(oldPath, vuePath));
          }
          if (properties?.$pathname) {
            json = json.replace(new RegExp(properties.$pathname, 'gi'), vuePath);
          }

          properties = JSON.parse(json);
        }

        if (event === '$pageleave') {
          // FIXME: Removed pending matching with vue routes
          properties.$prev_pageview_pathname = REMOVED_PROPERTY;
        }

        // Remove initial properties
        if (!properties.$set) {
          properties.$set = {};
        }

        properties.$set.$initial_current_url = REMOVED_PROPERTY;
        properties.$set.$initial_pathname = REMOVED_PROPERTY;

        // Remove initial person url
        if (properties?.$initial_person_info?.u) {
          properties.$initial_person_info.u = REMOVED_PROPERTY;
        }

        // Clean up webvitals
        // Ref: https://github.com/PostHog/posthog-js/blob/f5a0d12603197deab305a7e25843f04f3fa4c99e/src/extensions/web-vitals/index.ts#L175
        ['LCP', 'CLS', 'FCP', 'INP'].forEach((metric) => {
          if (properties[`$web_vitals_${metric}_event`]?.$current_url) {
            properties[`$web_vitals_${metric}_event`].$current_url = REMOVED_PROPERTY;
          }
        });

        return properties;
      },
    });
    posthog.register({
      service: 'apmt',
    });

    const id = await onPageLoad();
    if (user?.authenticated) {
      posthog.identify(user.data.uniqueHash);
    } else if (id) {
      posthog.identify(id);
    }
  }
});

</script>

<template>
  <!-- authenticated subscriber content -->
  <template v-if="router.hasRoute(route.name) && (user?.authenticated || routeIsPublic)">
    <site-notification
      v-if="user?.authenticated && visibleNotification"
      :title="notificationTitle"
      :action-url="notificationActionUrl"
    >
      {{ notificationMessage }}
    </site-notification>
    <nav-bar v-if="user?.authenticated" :nav-items="navItems"/>
    <title-bar v-if="routeIsPublic"/>
    <main
      :class="{
        'mx-4 min-h-full py-32 lg:mx-8': !routeIsHome && !routeIsPublic,
        '!pt-24': routeIsHome || user?.authenticated,
        'min-h-full': routeIsPublic && !routeHasModal,
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
