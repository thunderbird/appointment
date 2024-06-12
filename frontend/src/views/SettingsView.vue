<template>
  <!-- page title area -->
  <div class="flex select-none items-start justify-between">
    <div class="text-4xl font-light">{{ t('label.settings') }}</div>
  </div>
  <div class="mt-8 flex flex-col items-stretch justify-between gap-4 pb-2 lg:flex-row lg:gap-24 lg:pb-16">
    <!-- sidebar navigation -->
    <div class="mx-auto flex w-full flex-col gap-6 md:w-1/2 lg:w-full lg:max-w-60">
      <!-- search -->
      <label v-if="false" class="relative flex items-center">
        <icon-search
          class="
            absolute left-4 top-1/2 size-4 -translate-y-1/2 cursor-text fill-transparent stroke-gray-300
            stroke-2 dark:stroke-gray-500
          "
        />
        <input
          class="w-full rounded-md pl-12 pr-2 text-sm"
          type="search"
          name="search"
          :placeholder="t('label.search')"
        />
      </label>
      <!-- menu -->
      <div
        v-for="(view, key) in settingsSections"
        :key="key"
        class="
          btn-jump flex cursor-pointer justify-between rounded-lg bg-gray-100 p-4
          font-semibold text-gray-500 dark:bg-gray-600 dark:text-gray-300
        "
        :class="{ '!bg-teal-500 !text-white': view === activeView }"
        @click="show(key)"
      >
        <span>{{ t('label.' + key) }}</span>
        <icon-chevron-right
          class="
            size-6 rotate-180 fill-transparent stroke-gray-800 stroke-1 transition-transform
            dark:stroke-gray-300
          "
          :class="{ '!rotate-0 !stroke-white': view === activeView }"
        />
      </div>
    </div>
    <!-- content -->
    <div class="w-full pt-2 lg:w-4/5 lg:pt-14">
      <settings-general v-if="activeView === settingsSections.general" />
      <settings-calendar v-if="activeView === settingsSections.calendar" />
      <settings-account v-if="activeView === settingsSections.account" />
      <settings-connections v-if="activeView === settingsSections.connectedAccounts" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { settingsSections } from '@/definitions';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import SettingsGeneral from '@/components/SettingsGeneral';
import SettingsCalendar from '@/components/SettingsCalendar';

// icons
import {
  IconChevronRight,
  IconSearch,
} from '@tabler/icons-vue';
import SettingsAccount from '@/components/SettingsAccount.vue';
import SettingsConnections from '@/components/SettingsConnections.vue';

// component constants
const { t } = useI18n({ useScope: 'global' });
const route = useRoute();
const router = useRouter();

const activeView = computed(() => (route.params.view && settingsSections[route.params.view] ? settingsSections[route.params.view] : settingsSections.general));

// menu navigation of different views
const show = (key) => {
  router.push({ name: route.name, params: { view: key } });
};
</script>
