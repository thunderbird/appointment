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
          <div
            class="w-12 h-12 mr-4 self-center flex-center rounded-full text-lg bg-white font-normal text-white"
            :class="{'bg-teal-500': user.data.avatarUrl === null}"
          >
            <span v-if="user.data.avatarUrl === null">
              {{ initials(user.data.name) }}
            </span>
            <span v-else>
              <img class="rounded-full w-[48px] h-[48px]" :alt="initials(user.data.name)" :src="user.data.avatarUrl"/>
            </span>
          </div>
        </template>
        <template #default>
          <div class="flex flex-col gap-2 rounded-md w-48 p-4 bg-white dark:bg-gray-700 shadow-md">
            <router-link :to="{ name: 'profile' }" class="p-2">
              {{ t('label.userProfile') }}
            </router-link>
            <text-button
              v-show="signedUserUrl"
              :label="t('label.shareMyLink')"
              :copy="signedUserUrl"
              class="border-none flex-row-reverse justify-between !text-inherit !text-base !font-normal hover:bg-inherit hover:shadow-none"
            />
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
import { ref, inject, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { initials } from '@/utils';
import { useUserStore } from '@/stores/user-store';
import NavBarItem from "@/elements/NavBarItem";
import DropDown from "@/elements/DropDown";
import TextButton from "@/elements/TextButton";

// icons
import { IconExternalLink } from '@tabler/icons-vue';
// import { IconSearch } from '@tabler/icons-vue';

// component constants
const user = useUserStore();
const route = useRoute();
const { t } = useI18n();
const logout = inject('logout');
const call = inject('call');

// component properties
defineProps({
  navItems: Array, // list of route names that are also lang keys (format: label.<key>), used as nav items
});

const signedUserUrl = ref('');

const getSignedUserUrl = async () => {
  // Retrieve the user short url
  const { data, error } = await call('me/signature').get().json();
  if (error.value) {
    return;
  }

  signedUserUrl.value = data.value.url;
};

onMounted(async () => {
  await getSignedUserUrl();
});
</script>
