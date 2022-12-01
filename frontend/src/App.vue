<template>
  <template v-if="route.name === 'booking'">
    <router-view />
  </template>
  <template v-else>
    <nav-bar :nav-items="navItems" />
    <main class="mt-12 mx-8">
      <div class="w-full max-w-[1740px] mx-auto">
        <router-view />
      </div>
    </main>
  </template>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue';
import { useRoute } from 'vue-router';
const route = useRoute();

// menu items for main navigation
const navItems = ['calendar', 'appointments', 'settings'];
</script>
