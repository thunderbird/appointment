<template>
  <header
    class="
      fixed z-50 h-16 w-full px-4 shadow-lg border-b flex justify-between
      bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600
    "
  >
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
    <nav v-if="user.exists()" class="flex gap-4 items-stretch">
      <div class="flex justify-end gap-8">
        <nav-bar-item
          v-for="item in navItems"
          :key="item"
          :active="route.name == item"
          :label="t(`label.${item}`)"
          :link-name="item"
        />
      </div>
      <drop-down class="self-center">
        <template #trigger>
          <avatar />
        </template>
        <template #default>
          <div class="flex flex-col gap-2 rounded-md w-48 p-4 bg-white dark:bg-gray-700 shadow-md">
            <router-link :to="{ name: 'profile' }" class="p-2">
              {{ t('label.userProfile') }}
            </router-link>
            <text-button
              v-show="user.data.signedUrl"
              :label="t('label.shareMyLink')"
              :copy="user.data.signedUrl"
              class="border-none flex-row-reverse justify-between !text-inherit !text-base !font-normal hover:bg-inherit hover:shadow-none"
            />
            <router-link :to="{ name: 'contact' }" class="p-2">
              {{ t('label.contact') }}
            </router-link>
            <hr class="border-teal-500" />
            <div @click="logout" class="cursor-pointer p-2">
              {{ t('label.logOut') }}
            </div>
          </div>
        </template>
      </drop-down>
    </nav>
  </header>
</template>

<script setup>
import { inject } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user-store';
import Avatar from '@/elements/Avatar';
import DropDown from '@/elements/DropDown';
import NavBarItem from '@/elements/NavBarItem';
import TextButton from '@/elements/TextButton';

// component constants
const user = useUserStore();
const route = useRoute();
const router = useRouter();
const { t } = useI18n();
const call = inject('call');

// component properties
defineProps({
  navItems: Array, // list of route names that are also lang keys (format: label.<key>), used as nav items
});

// do log out
const logout = async () => {
  await user.logout(call);
  await router.push('/');
};
</script>
