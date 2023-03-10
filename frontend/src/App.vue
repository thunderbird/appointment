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
import { ref, inject, provide, onMounted, computed } from 'vue';
import { useAuth0 } from '@auth0/auth0-vue';
import { useRoute } from 'vue-router';
import NavBar from '@/components/NavBar';
import TitleBar from '@/components/TitleBar';

// component constants
const auth0 = useAuth0();
const route = useRoute();
const call = inject('call');
const dj = inject('dayjs');

// menu items for main navigation
const navItems = ['calendar', 'appointments', 'settings'];

// current user object
// TODO: structure: { username, email, name, level, timezone, id }
const currentUser = ref(null);

// db tables
const calendars = ref([]);
const appointments = ref([]);

// true if route can be accessed without authentication
const routeIsPublic = computed(() => {
  return route.name === 'booking' || (route.name === 'home' && !auth0.isAuthenticated.value);
});

// check login state of current user first
const checkLogin = async () => {
  currentUser.value = auth0.user.value;
  // TODO: call backend to create user if they do not exist in database
  // const { data } = await call("login").get().json();
};

// query db for all calendar and appointments data
const getDbCalendars = async () => {
  const { data } = await call("me/calendars").get().json();
  calendars.value = data.value;
};
const getDbAppointments = async () => {
  const { data } = await call("me/appointments").get().json();
  appointments.value = data.value;
  // extend appointments data with active state and calendar title and color
  const calendarsById = {};
  calendars.value?.forEach(c => { calendarsById[c.id] = c });
  appointments.value?.forEach(a => {
    a.calendar_title = calendarsById[a.calendar_id]?.title;
    a.calendar_color = calendarsById[a.calendar_id]?.color;
    a.status = getAppointmentStatus(a);
    a.active = a.status !== appointmentState.past; // TODO
  });
};
const getDbData = async () => {
  await checkLogin();
  if (auth0.isAuthenticated.value) {
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
  if (a.slots.filter(s => s.attendee != null).length > 0) {
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
