<template>
  <header class="h-24 shadow-lg border-b border-gray-300 flex justify-between">
    <router-link class="py-7 pl-8 pr-12 border-r" :to="{ name: 'calendar' }">
      <img class="h-full" src="/appointment_logo.svg" alt="Appointment Logo">
    </router-link>
    <label class="grow flex items-center">
      <img class="h-6 w-6 ml-8 mr-4" src="@/assets/icon-search.svg" alt="Search Icon">
      <input class="w-full h-full text-xl px-2" type="search" name="search" :placeholder="t('label.search')">
    </label>
    <nav class="flex gap-8 items-stretch">
      <ul class="flex justify-end gap-8">
        <li
          v-for="item in navItems"
          :key="item"
          class="flex text-xl border-b-4 border-b-transparent"
          :class="{
            'font-semibold border-b-teal-500 text-teal-500': route.name == item,
            'text-gray-700': route.name != item,
          }"
        >
          <router-link class="flex justify-center min-w-[130px] items-center" :to="{ name: item }">
            {{ t('label.' + item) }}
          </router-link>
        </li>
      </ul>
      <router-link
        :to="{ name: 'profile' }"
        class="w-12 h-12 mx-8 self-center flex justify-center items-center rounded-full bg-teal-500 text-lg font-bold text-white"
      >
        JD
      </router-link>
    </nav>
  </header>
</template>

<script setup>
import { useRoute } from 'vue-router';
import { useI18n } from "vue-i18n";
const route = useRoute();
const { t } = useI18n();

// define which navigation items to show
const navItems = ['calendar', 'events', 'settings'];
</script>
