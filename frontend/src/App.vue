<template>
  <!-- authenticated subscriber content -->
  <template v-if="isAuthenticated">
    <site-notification
      v-if="siteNotificationStore.isVisible"
      :title="siteNotificationStore.title"
      :action-url="siteNotificationStore.actionUrl"
    >
      {{ siteNotificationStore.message }}
    </site-notification>
    <nav-bar :nav-items="navItems" />
    <main :class="{'mx-4 pt-24 lg:mx-8 min-h-full pb-24': !routeIsHome, 'pt-32': routeIsHome}">
      <router-view />
    </main>
    <footer-bar />
  </template>
  <!-- for home page and booking page -->
  <template v-else-if="routeIsPublic">
    <title-bar />
    <main class="min-h-full">
      <router-view />
    </main>
    <footer-bar />
  </template>
  <template v-else>
    <!-- TODO: handle wrong route -->
    An authentication or routing error occurred.
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

// stores
import { useUserStore } from '@/stores/user-store';
import { useCalendarStore } from '@/stores/calendar-store';
import { useAppointmentStore } from '@/stores/appointment-store';

// component constants
const currentUser = useUserStore(); // data: { username, email, name, level, timezone, id }
const apiUrl = inject('apiUrl');
const route = useRoute();
const router = useRouter();
const siteNotificationStore = useSiteNotificationStore();

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
    async onFetchError({ data, response, error }) {
      // Catch any google refresh error that may occur
      if (
        data?.detail?.id === 'GOOGLE_REFRESH_ERROR'
        && !siteNotificationStore.isSameNotification('GOOGLE_REFRESH_ERROR')
      ) {
        // Ensure other async calls don't reach here
        siteNotificationStore.lock(data.detail.error);

        // Retrieve the google auth url, and if that fails send them to calendar settings!
        const { data: urlData, error: urlError } = await call('google/auth').get();
        const url = urlError.value ? '/settings/calendar' : urlData.value.slice(1, -1);

        // Update our site notification store with the error details
        siteNotificationStore.show(
          data.detail.error,
          'Action needed!',
          data.detail?.message || 'Please re-connect with Google',
          url,
        );
      } else if (response.status === 401 && data?.detail?.id === 'INVALID_TOKEN') {
        // Clear current user data, and ship them to the login screen!
        await currentUser.reset();
        await router.push('/login');
        return;
      }

      // Pass the error along
      return { data, response, error };
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

// true if route can be accessed without authentication
const routeIsPublic = computed(
  () => ['booking', 'availability', 'home', 'login', 'post-login'].includes(route.name),
);
const routeIsHome = computed(
  () => ['home'].includes(route.name),
);

// check appointment status for current state (past|pending|booked)
const getAppointmentStatus = (a) => appointmentStore.status(a);

// retrieve calendars and appointments after checking login and persisting user to db
const getDbData = async () => {
  if (currentUser?.exists()) {
    await Promise.all([
      calendarStore.fetch(call),
      appointmentStore.fetch(call),
    ]);
  }
};

// provide refresh functions for components
provide('refresh', getDbData);
provide('getAppointmentStatus', getAppointmentStatus);
</script>
