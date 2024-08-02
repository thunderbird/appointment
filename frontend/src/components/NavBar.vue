<script setup lang="ts">
import { inject } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user-store';
import { callKey } from '@/keys';
import UserAvatar from '@/elements/UserAvatar.vue';
import DropDown from '@/elements/DropDown.vue';
import NavBarItem from '@/elements/NavBarItem.vue';
import TextButton from '@/elements/TextButton.vue';

// component constants
const user = useUserStore();
const route = useRoute();
const router = useRouter();
const { t } = useI18n();
const call = inject(callKey);

// component properties
interface Props {
  navItems: string[], // list of route names that are also lang keys (format: label.<key>), used as nav items
};
defineProps<Props>();

// do log out
const logout = async () => {
  await user.logout(call);
  await router.push('/');
};
</script>

<template>
  <header
    class="
      fixed z-50 flex h-16 w-full justify-between overflow-x-auto overflow-y-visible border-b border-gray-300
      bg-white px-4 shadow-lg dark:border-gray-600 dark:bg-gray-700 md:overflow-visible
    "
  >
    <router-link
      class="shrink-0 border-r border-gray-300 py-4 pl-4 pr-8 dark:border-gray-600"
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
    <nav v-if="user.exists()" class="flex items-stretch gap-4">
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
          <user-avatar />
        </template>
        <template #default>
          <div class="fixed left-0 top-16 flex w-full flex-col gap-2 rounded-md bg-white p-4 shadow-md dark:bg-gray-700 md:static md:left-auto md:top-auto md:w-48">
            <router-link :to="{ name: 'profile' }" class="p-2">
              {{ t('label.userProfile') }}
            </router-link>
            <text-button
              v-show="user.myLink"
              :label="t('label.shareMyLink')"
              :copy="user.myLink"
              :title="t('label.copy')"
              class="btn-copy flex-row-reverse justify-between border-none !text-base !font-normal !text-inherit hover:bg-inherit hover:shadow-none"
            />
            <router-link :to="{ name: 'contact' }" class="p-2">
              {{ t('label.contact') }}
            </router-link>
            <hr class="border-teal-500" />
            <div @click="logout" class="btn-logout cursor-pointer p-2" :title="t('label.logOut')">
              {{ t('label.logOut') }}
            </div>
          </div>
        </template>
      </drop-down>
    </nav>
  </header>
</template>
