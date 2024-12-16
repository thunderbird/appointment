<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user-store';
import UserAvatar from '@/elements/UserAvatar.vue';
import DropDown from '@/elements/DropDown.vue';
import NavBarItem from '@/elements/NavBarItem.vue';
import TextButton from '@/elements/TextButton.vue';
import { IconExternalLink } from '@tabler/icons-vue';

// component constants
const user = useUserStore();
const route = useRoute();
const { t } = useI18n();

// component properties
interface Props {
  navItems: string[], // list of route names that are also lang keys (format: label.<key>), used as nav items
}
defineProps<Props>();

/**
 * Is this nav entry active?
 * @param item
 */
const isNavEntryActive = (item: string) => {
  // Hack for FTUE!
  if (item === 'dashboard' && route.name === 'setup') {
    return true;
  }
  return route.name === item;
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
      :to="{ name: 'dashboard' }"
    >
      <img class="h-8" src="@/assets/svg/appointment_logo_beta.svg" alt="Appointment Logo" />
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
          :active="isNavEntryActive(item)"
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
              uid="myLink"
              :label="t('navBar.shareMyLink')"
              :copy="user.myLink"
              :title="t('label.copy')"
              class="btn-copy flex-row-reverse justify-between border-none !text-base !font-normal !text-inherit hover:bg-inherit hover:shadow-none"
              data-testid="user-nav-share-link-btn"
            />
            <router-link :to="{ name: 'report-bug' }" class="flex items-center justify-between gap-1 p-2" data-testid="user-nav-report-bug-menu">
              {{ t('navBar.reportBug') }} <icon-external-link class="size-4"/>
            </router-link>
            <router-link :to="{ name: 'contact' }" class="p-2" data-testid="user-nav-contact-menu">
              {{ t('label.contact') }}
            </router-link>
            <hr class="border-teal-500" />
            <router-link :to="{ name: 'logout' }" class="p-2" data-testid="user-nav-logout-menu">
              {{ t('label.logOut') }}
            </router-link>
          </div>
        </template>
      </drop-down>
    </nav>
  </header>
</template>
