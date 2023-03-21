<template>
  <!-- public booking link -->
  <template v-if="routeIsPublic">
    <title-bar />
    <router-view />
  </template>
  <!-- authenticated subscriber content -->
  <template v-else>
    <nav-bar :nav-items="navItems" :user="currentUser" />
    <main class="mt-12 mx-4 lg:mx-8">
      <div class="w-full max-w-[1740px] mx-auto">
        <router-view :calendars="calendars" :appointments="appointments" :user="currentUser" />
      </div>
    </main>
  </template>
</template>

<script setup>
import { appointmentState } from '@/definitions';
import { createFetch } from '@vueuse/core'
import { ref, inject, provide, onMounted, computed } from 'vue';
import { useAuth0 } from '@auth0/auth0-vue';
import { useRoute } from 'vue-router';
import NavBar from '@/components/NavBar';
import TitleBar from '@/components/TitleBar';

// component constants
const apiUrl = inject('apiUrl');
const dj = inject('dayjs');
const route = useRoute();

// handle auth and fetch
const auth = useAuth0();
const call = createFetch({
  baseUrl: apiUrl,
  options: {
    async beforeFetch({ options }) {
      if (auth.isAuthenticated.value) {
        const token = await auth.getAccessTokenSilently();
        options.headers.Authorization = `Bearer ${token}`;
        // options.headers.SetCookie = 'SameSite=None; Secure'; // can be adjusted if necessary
      }
      return { options };
    },
  },
  fetchOptions: {
    mode: 'cors',
  },
})
provide('auth', auth);
provide('call', call);

// menu items for main navigation
const navItems = ['calendar', 'appointments', 'settings'];

// current user object
// structure: { username, email, name, level, timezone, id }
const currentUser = ref(null);

// db tables
const calendars = ref([]);
const appointments = ref([]);

// true if route can be accessed without authentication
const routeIsPublic = computed(() => {
  return route.name === 'booking' || (route.name === 'home' && !auth.isAuthenticated.value);
});

// check login state of current user first
const checkLogin = async () => {
  if (auth.isAuthenticated.value) {
    // call backend to create user if they do not exist in database
    const { data, error} = await call("login").get().json();
    // assign authed user data
    if (!error.value && data.value) {
      // data.value holds appointment subscriber structure
      // auth.user.value holds auth0 user structure
      currentUser.value = data.value;
    }
  }
};

// query db for all calendar and appointments data
const getDbCalendars = async () => {
  const { data, error } = await call("me/calendars").get().json();
  if (!error.value) {
    calendars.value = data.value;
  }
};
const getDbAppointments = async () => {
  const { data, error } = await call("me/appointments").get().json();
  if (!error.value) {
    appointments.value = data.value;
  }
  // extend appointments data with active state and calendar title and color
  const calendarsById = {};
  calendars.value.forEach(c => { calendarsById[c.id] = c });
  appointments.value.forEach(a => {
    a.calendar_title = calendarsById[a.calendar_id]?.title;
    a.calendar_color = calendarsById[a.calendar_id]?.color;
    a.status = getAppointmentStatus(a);
    a.active = a.status !== appointmentState.past; // TODO
  });
};
const getDbData = async () => {
  await checkLogin();
  if (auth.isAuthenticated.value) {
    await getDbCalendars();
    await getDbAppointments();
  }
}

// check appointment status for current state (past|pending|booked)
const getAppointmentStatus = (a) => {
  // check past events
  if (a.slots.filter(s => dj(s.start).isAfter(dj())).length === 0) {
    return appointmentState.past;
  }
  // check booked events
  if (a.slots.filter(s => s.attendee_id != null).length > 0) {
    return appointmentState.booked;
  }
  // else event is still wating to be booked
  return appointmentState.pending;
}

// get the data initially
onMounted(async () => {
  await getDbData();
})

// provide refresh functions for components
provide('refresh', getDbData);
provide('getAppointmentStatus', getAppointmentStatus);
</script>
