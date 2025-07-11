<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user-store';
import UserAvatar from '@/elements/UserAvatar.vue';
import DropDown from '@/elements/DropDown.vue';
import NavBarItem from '@/elements/NavBarItem.vue';
import TextButton from '@/elements/TextButton.vue';
import ToolTip from '@/tbpro/elements/ToolTip.vue';
import { TooltipPosition } from '@/definitions';
import { IconExternalLink, IconLink } from '@tabler/icons-vue';

// component constants
const user = useUserStore();
const route = useRoute();
const { t } = useI18n();

// component properties
interface Props {
  navItems: string[], // list of route names that are also lang keys (format: label.<key>), used as nav items
}
defineProps<Props>();

const profileDropdown = ref();
const myLinkTooltip = ref(t('label.copyLink'));

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

// Link copy
const copyLink = async () => {
  await navigator.clipboard.writeText(user.myLink);

  myLinkTooltip.value = t('info.copiedToClipboard');

  setTimeout(() => {
    myLinkTooltip.value = t('label.copyLink');
  }, 2000);
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
      :to="{ name: user?.authenticated ? 'dashboard' : 'home' }"
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
    <nav v-if="user.authenticated" class="flex items-stretch gap-4">
      <div class="flex justify-end gap-8">
        <nav-bar-item
          v-for="item in navItems"
          :key="item"
          :active="isNavEntryActive(item)"
          :label="t(`label.${item}`)"
          :link-name="item"
        />
        <div v-if="user.myLink" class="flex items-center justify-center px-4 relative">
          <button
            class="cursor-pointer bg-transparent border-none font-semibold min-w-0 p-0 flex items-center relative group active:text-teal-500"
            @click="copyLink"
            aria-labelledby="copy-meeting-link-button"
          >
            <icon-link id="copy-meeting-link-button"></icon-link>
            <tool-tip
              :position="TooltipPosition.Top"
              class="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 opacity-0 transition-opacity duration-250 ease-out group-hover:opacity-100 group-hover:pointer-events-auto whitespace-nowrap text-xs min-w-max"
            >
              {{ myLinkTooltip }}
            </tool-tip>
          </button>
        </div>
      </div>

      <drop-down class="self-center" ref="profileDropdown">
        <template #trigger>
          <div class="flex items-center gap-4 border rounded-md border-gray-300 pl-3 pr-1 py-1 bg-white">
            <span class="text-sm text-gray-500">
              {{ user.data.email }}
            </span>

            <user-avatar />
          </div>
        </template>
        <template #default>
          <div
            @click="profileDropdown.close()"
            class="fixed left-0 top-16 flex w-full flex-col gap-2 rounded-md bg-white p-4 shadow-md dark:bg-gray-700 md:static md:left-auto md:top-auto md:w-48"
          >
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
            <router-link :to="{ name: 'contact' }" class="flex items-center justify-between gap-1 p-2" data-testid="user-nav-contact-menu">
              {{ t('label.contact') }} <icon-external-link class="size-4"/>
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
