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
      <router-view
        :calendars="calendars"
        :appointments="appointments"
      />
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
import { appointmentState } from "@/definitions";
import { createFetch } from "@vueuse/core";
import { ref, inject, provide, onMounted, computed } from "vue";
import { useRoute } from "vue-router";
import NavBar from "@/components/NavBar";
import TitleBar from "@/components/TitleBar";
import FooterBar from "@/components/FooterBar.vue";
import SiteNotification from "@/elements/SiteNotification";
import { useSiteNotificationStore } from "@/stores/alert-store";

// stores
import { useUserStore } from '@/stores/user-store';

// component constants
const currentUser = useUserStore(); // data: { username, email, name, level, timezone, id }
const apiUrl = inject("apiUrl");
const dj = inject("dayjs");
const route = useRoute();
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
        data?.detail?.error === 'google_refresh_error' &&
        !siteNotificationStore.isSameNotification('google_refresh_error')
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
      } else if (error.statusCode === 401) {
        console.log("FAILED, PLS LOGIN");
        // Clear current user data, and ship them to the login screen!
        await currentUser.reset();
        window.location = '/login';
      }

      // Pass the error along
      return { data, response, error };
    },
  },
  fetchOptions: {
    mode: "cors",
    credentials: "include",
  },
});
provide("call", call);

// menu items for main navigation
const navItems = [
  "calendar",
  "schedule",
  "appointments",
  "settings",
];

// db tables
const calendars = ref([]);
const appointments = ref([]);

// true if route can be accessed without authentication
const routeIsPublic = computed(
  () => ['booking', 'availability', 'home', 'login', 'post-login'].includes(route.name),
);
const routeIsHome = computed(
  () => ['home'].includes(route.name),
);

// query db for all calendar data
const getDbCalendars = async (onlyConnected = true) => {
  const { data, error } = await call(`me/calendars?only_connected=${onlyConnected}`).get().json();
  if (!error.value) {
    if (data.value === null || typeof data.value === "undefined") return;
    calendars.value = data.value;
  }
};
// query db for all appointments data
const getDbAppointments = async () => {
  const { data, error } = await call("me/appointments").get().json();
  if (!error.value) {
    if (data.value === null || typeof data.value === "undefined") return;
    appointments.value = data.value;
  }
};

// check appointment status for current state (past|pending|booked)
const getAppointmentStatus = (a) => {
  // check past events
  if (a.slots.filter((s) => dj(s.start).isAfter(dj())).length === 0) {
    return appointmentState.past;
  }
  // check booked events
  if (a.slots.filter((s) => s.attendee_id != null).length > 0) {
    return appointmentState.booked;
  }
  // else event is still wating to be booked
  return appointmentState.pending;
};

// extend retrieved data
const extendDbData = () => {
  // build { calendarId => calendarData } object for direct lookup
  const calendarsById = {};
  calendars.value.forEach((c) => {
    calendarsById[c.id] = c;
  });
  // extend appointments data with active state and calendar title and color
  appointments.value.forEach((a) => {
    a.calendar_title = calendarsById[a.calendar_id]?.title;
    a.calendar_color = calendarsById[a.calendar_id]?.color;
    a.status = getAppointmentStatus(a);
    a.active = a.status !== appointmentState.past; // TODO
    // convert start dates from UTC back to users timezone
    a.slots.forEach((s) => {
      s.start = dj.utc(s.start).tz(currentUser.data.timezone ?? dj.tz.guess());
    });
  });
};

// retrieve calendars and appointments after checking login and persisting user to db
const getDbData = async (options = {}) => {
  const { onlyConnectedCalendars = true } = options;

  if (currentUser?.exists()) {
    await Promise.all([
      getDbCalendars(onlyConnectedCalendars),
      getDbAppointments(),
    ]);
    extendDbData();
  }
};

// get the data initially
onMounted(async () => {
  await getDbData();
});

// provide refresh functions for components
provide("refresh", getDbData);
provide("getAppointmentStatus", getAppointmentStatus);
</script>
