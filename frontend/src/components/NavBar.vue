<template>
  <header class="h-16 px-4 shadow-lg border-b flex justify-between border-gray-300 dark:border-gray-600">
    <router-link
      class="py-4 pl-4 pr-8 border-r border-gray-300 dark:border-gray-600 shrink-0"
      :to="{ name: 'calendar' }"
    >
      <img class="h-8" src="/appointment_logo.svg" alt="Appointment Logo" />
    </router-link>
    <!-- <label class="grow flex items-center relative">
      <icon-search
        class="
          absolute top-1/2 -translate-y-1/2 left-7 cursor-text h-8 w-8 stroke-2 fill-transparent
          stroke-gray-300 dark:stroke-gray-500
        "
      />
      <input
        class="w-full h-full text-xl pl-20 pr-2 border-none"
        type="search"
        name="search"
        :placeholder="t('label.search')"
      />
    </label> -->
    <nav class="flex gap-4 items-stretch">
      <ul class="flex justify-end gap-8">
        <li
          v-for="item in navItems"
          :key="item"
          class="flex text-base border-b-4 border-b-transparent transition-all ease-in-out"
          :class="{
            'font-semibold border-b-teal-500 text-teal-500': route.name == item,
            'text-gray-600 dark:text-gray-300 hover:border-b-gray-200 dark:hover:border-b-gray-400':
              route.name != item,
          }"
        >
          <router-link class="flex justify-center min-w-[120px] items-center" :to="{ name: item }">
            {{ t("label." + item) }}
          </router-link>
        </li>
      </ul>
      <router-link
        v-if="user"
        :to="{ name: 'profile' }"
        class="w-12 h-12 mr-4 self-center flex-center rounded-full bg-teal-500 text-lg font-normal text-white"
      >
        {{ initials(user.name) }}
      </router-link>
    </nav>
  </header>
</template>

<script setup>
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { initials } from '@/utils';

// icons
// import { IconSearch } from '@tabler/icons-vue';

// component constants
const route = useRoute();
const { t } = useI18n();

// component properties
defineProps({
  navItems: Array, // list of route names that are also lang keys (format: label.<key>), used as nav items
  user: Object, // currently logged in user, null if not logged in
});
</script>
