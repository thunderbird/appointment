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
        'min-h-full pt-8 pb-32': routeIsPublic,
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
import { inject, provide, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import NavBar from '@/components/NavBar';
import TitleBar from '@/components/TitleBar';
import FooterBar from '@/components/FooterBar.vue';
import SiteNotification from '@/elements/SiteNotification';
import { useSiteNotificationStore } from '@/stores/alert-store';
import { storeToRefs } from 'pinia';

// stores
import { useUserStore } from '@/stores/user-store';
import { useCalendarStore } from '@/stores/calendar-store';
import { useAppointmentStore } from '@/stores/appointment-store';
import { useScheduleStore } from '@/stores/schedule-store';
import RouteNotFoundView from '@/views/errors/RouteNotFoundView.vue';
import NotAuthenticatedView from '@/views/errors/NotAuthenticatedView.vue';

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
  isSame: isSameNotification,
  lock: lockNotification,
  show: showNotification,
} = storeToRefs(siteNotificationStore);

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
      } else if (response.status === 401 && data?.detail?.id === 'INVALID_TOKEN') {
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
provide('call', call);
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

// true if route can be accessed without authentication
const routeIsPublic = computed(
  () => ['booking', 'availability', 'home', 'login', 'post-login', 'confirmation'].includes(route.name),
);
const routeIsHome = computed(
  () => ['home'].includes(route.name),
);

// retrieve calendars and appointments after checking login and persisting user to db
const getDbData = async () => {
  if (currentUser?.exists()) {
    await Promise.all([
      calendarStore.fetch(call),
      appointmentStore.fetch(call),
      scheduleStore.fetch(call),
    ]);
  }
};

// provide refresh functions for components
provide('refresh', getDbData);
</script>
