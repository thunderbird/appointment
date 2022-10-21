<template>
  <header class="h-24 shadow-lg border-b border-gray-300 flex justify-between">
    <router-link class="py-7 pl-8 pr-12 border-r" :to="{ name: 'calendar' }">
      <img class="h-10" src="/appointment_logo.svg" alt="Appointment Logo">
    </router-link>
    <label class="grow flex items-center relative">
      <icon-search class="absolute top-1/2 -translate-y-1/2 left-7 cursor-text h-8 w-8 stroke-2 stroke-gray-300 fill-transparent" /> 
      <input class="w-full h-full text-xl pl-20 pr-2 border-none" type="search" name="search" :placeholder="t('label.search')">
    </label>
    <nav class="flex gap-8 items-stretch">
      <ul class="flex justify-end gap-8">
        <li
          v-for="item in navItems"
          :key="item"
          class="flex text-xl border-b-4 border-b-transparent transition-all ease-in-out"
          :class="{
            'font-semibold border-b-teal-500 text-teal-500': route.name == item,
            'text-gray-600 hover:border-b-gray-200': route.name != item,
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
import IconSearch from '@/elements/icons/IconSearch.vue';
import { useRoute } from 'vue-router';
import { useI18n } from "vue-i18n";
const route = useRoute();
const { t } = useI18n();

// component properties
defineProps({
  navItems: Array // list of route names that are also lang keys (format: label.<key>), used as nav items
});
</script>
