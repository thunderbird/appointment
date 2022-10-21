<template>
  <nav-bar :nav-items="navItems" />
  <main class="mt-12 mx-8">
    <div class="w-full max-w-[1740px] mx-auto">
      <router-view />
    </div>
  </main>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue';

// menu items for main navigation
const navItems = ['calendar', 'events', 'settings'];
</script>
