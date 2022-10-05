<template>
  <NavBar />
  <div class="w-full max-w-[1740px] mx-auto mt-8">
    <router-view/>
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue';
</script>
