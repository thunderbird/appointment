<script setup lang="ts">
import {
  computed, onMounted, ref, watch,
} from 'vue';
import { SettingsSections } from '@/definitions';
import { enumToObject } from '@/utils';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user-store';
import SettingsCalendar from './components/SettingsCalendar.vue';
import SettingsConnections from './components/SettingsConnections.vue';

// icons
import {
  IconChevronRight,
  IconSearch,
} from '@tabler/icons-vue';

import AccountSettings from './components/AccountSettings.vue';
import Preferences from './components/Preferences.vue';
import ConnectedApplications from './components/ConnectedApplications.vue';

// component constants
const { t } = useI18n({ useScope: 'global' });
const route = useRoute();
const router = useRouter();
const sections = ref(enumToObject(SettingsSections));
// Note: Use direct variables in computed, otherwise it won't be updated if transformed (like by typing)
const activeView = computed<number>(() => (route.params.view && sections.value[route.params.view as string] ? sections.value[route.params.view as string] : SettingsSections.AccountSettings));
const user = useUserStore();

// menu navigation of different views
const show = (key: string) => {
  router.push({ name: route.name, params: { view: key } });
};

/**
 * If the user isn't setup, redirect them to account
 * @param view
 */
const redirectSetupUsers = (view: string) => {
  if (!view) {
    return;
  }
  if (view !== 'account') {
    router.replace({ name: 'settings', params: { view: 'account' } });
  }
};

onMounted(() => {
  if (!user?.data.isSetup) {
    // If we're not setup watch (and initially apply) the view param
    watch(() => route.params.view, (val) => {
      redirectSetupUsers(val as string);
    });
    redirectSetupUsers(route.params.view as string);

    // Restrict settings to just the account settings
    sections.value = {
      account: SettingsSections.AccountSettings,
    };
  }
});
</script>

<script lang="ts">
export default {
  name: 'SettingsView'
}
</script>

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
        v-for="(view, key) in sections"
        :key="key"
        class="
          btn-jump flex cursor-pointer justify-between rounded-lg bg-gray-100 p-4
          font-semibold text-gray-500 dark:bg-gray-600 dark:text-gray-300
        "
        :class="{ '!bg-teal-500 !text-white': view === activeView }"
        @click="show(key)"
        :data-testid="'settings-' + key + '-settings-btn'"
      >
        <span>{{ t('label.' + key) }}</span>
        <icon-chevron-right
          class="
            size-6 rotate-0 fill-transparent stroke-gray-800 stroke-1 transition-transform
            dark:stroke-gray-300
          "
        />
      </div>
    </div>
    <!-- content -->
    <div class="w-full lg:w-4/5">
      <section id="accountSettings">
        <account-settings />
      </section>

      <section id="preferences">
        <preferences />
      </section>

      <section id="connectedApplications">
        <connected-applications />
      </section>

      <settings-calendar />
      <settings-connections />
    </div>
  </div>
</template>

<style scoped>
section {
  border: 1px solid var(--colour-neutral-border);
  border-radius: 8px;
  padding: 1.5rem;
  align-self: flex-start;
  background-color: var(--colour-neutral-lower);
  margin-block-end: 2rem;
}
</style>