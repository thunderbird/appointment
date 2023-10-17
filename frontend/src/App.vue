<template>
  <!-- authenticated subscriber content -->
  <template v-if="isAuthenticated">
    <site-notification
      v-if="siteNotificationStore.display"
      :title="siteNotificationStore.title"
      :action-url="siteNotificationStore.actionUrl"
    >
      {{ siteNotificationStore.message }}
    </site-notification>
    <nav-bar :nav-items="navItems" />
    <main class="mx-4 pt-24 lg:mx-8 min-h-full">
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
    <main class="mx-4 pt-24 lg:mx-8 min-h-full">
      <router-view />
    </main>
    <footer-bar />
  </template>
  <template v-else>
    <!-- TODO: handle wrong route -->
    A authentication or routing error occurred.
  </template>
</template>

<script setup>
import { appointmentState } from "@/definitions";
import { createFetch } from "@vueuse/core";
import { ref, inject, provide, onMounted, computed } from "vue";
import { useAuth0 } from "@auth0/auth0-vue";
import { useRoute } from "vue-router";
import NavBar from "@/components/NavBar";
import TitleBar from "@/components/TitleBar";
import SiteNotification from "@/elements/SiteNotification";
import { siteNotificationStore } from "@/stores/alert-store";

// stores
import { useUserStore } from '@/stores/user-store';
import FooterBar from "@/components/FooterBar.vue";

// component constants
const currentUser = useUserStore(); // data: { username, email, name, level, timezone, id }
const apiUrl = inject("apiUrl");
const dj = inject("dayjs");
const route = useRoute();

// handle auth and fetch
const auth = useAuth0();
const isAuthenticated = computed(() => auth.isAuthenticated.value);
const call = createFetch({
  baseUrl: apiUrl,
  options: {
    async beforeFetch({ options }) {
      if (auth.isAuthenticated.value) {
        try {
          const token = await auth.getAccessTokenSilently();
          options.headers.Authorization = `Bearer ${token}`;
        } catch (e) {
          // TODO: prompt the user to re-login here due to auth0 error
          // console.warn('Failed to apply bearer token', e);
        }
        // options.headers.SetCookie = 'SameSite=None; Secure'; // can be adjusted if necessary
      }
      return { options };
    },
    async onFetchError({ data, response, error }) {
      // Catch any google refresh error that may occur
      if (
        data?.detail?.error === "google_refresh_error" &&
        siteNotificationStore.value.id !== "google_refresh_error"
      ) {
        // Ensure other async calls don't reach here
        siteNotificationStore.value.id = data.detail.error;

        // Retrieve the google auth url, and if that fails send them to calendar settings!
        const { data: urlData, error: urlError } = await call('google/auth').get();
        const url = urlError.value ? '/settings/calendar' : urlData.value.slice(1, -1);

        // Update our site notification store with the error details
        siteNotificationStore.value = {
          id: data.detail.error,
          display: true,
          actionUrl: url,
          title: "Action needed!",
          message: data.detail?.message || "Please re-connect with Google",
        };
      }

      // Pass the error along
      return { data, response, error };
    },
  },
  fetchOptions: {
    mode: "cors",
  },
});
provide("auth", auth);
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
  () => ["booking", "availability", "home"].includes(route.name)
);

// check login state of current user first
const checkLogin = async () => {
  console.log(auth.user.value, currentUser.data);
  if (auth.isAuthenticated.value) {
    if (currentUser.exists() && currentUser.data.email === auth.user.value.email) {
      // avoid calling the backend unnecessarily
      return;
    }
    // call backend to create user if they do not exist in database
    const { data, error } = await call("login").get().json();
    // assign authed user data
    if (!error.value && data.value) {
      // data.value holds appointment subscriber structure
      // auth.user.value holds auth0 user structure
      currentUser.$patch({ data: data.value });
    } else if (data.value && data.value.detail === "Missing bearer token") {
      // Try logging in if we have an expired refresh token, but a valid authentication id.
      await auth.loginWithRedirect();
    }
  }
};

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

  await checkLogin();
  if (auth.isAuthenticated.value) {
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
