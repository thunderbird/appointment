<template>
  <!-- public booking link -->
  <template v-if="route.name === 'booking'">
    <router-view />
  </template>
  <!-- authenticated subscriber content -->
  <template v-else>
    <nav-bar :nav-items="navItems" />
    <main class="mt-12 mx-8">
      <div class="w-full max-w-[1740px] mx-auto">
        <router-view v-if="routeNeedsData" :calendars="calendars" :appointments="appointments" />
        <router-view v-else />
      </div>
    </main>
  </template>
</template>

<script setup>
import { ref, inject, provide, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import NavBar from '@/components/NavBar';

const route = useRoute();
const call = inject('call');

// menu items for main navigation
const navItems = ['calendar', 'appointments', 'settings'];

// db tables
const calendars = ref([]);
const appointments = ref([]);

// define which routes need data from db
const routeNeedsData = computed(() => {
  return ['calendar', 'appointments', 'settings'].includes(route.name);
});

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
  calendars.value.forEach(c => { calendarsById[c.id] = c });
  appointments.value.forEach(a => {
    a.calendar_title = calendarsById[a.calendar_id]?.title;
    a.calendar_color = calendarsById[a.calendar_id]?.color;
    a.active = a.status == 2; // TODO
  });
};
const getDbData = async () => {
  if (routeNeedsData.value) {
    await getDbCalendars();
    await getDbAppointments();
  }
}

// get the data initially
onMounted(() => {
  getDbData();
})

// provide refresh functions for components
provide('refresh', getDbData);
</script>
