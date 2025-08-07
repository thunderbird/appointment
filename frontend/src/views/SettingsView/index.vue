<script setup lang="ts">
import {
  computed, onMounted, ref, watch,
} from 'vue';
import { SettingsSections } from '@/definitions';
import { enumToObject } from '@/utils';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user-store';
import { IconChevronRight } from '@tabler/icons-vue';

// Page sections
import AccountSettings from './components/AccountSettings.vue';
import Preferences from './components/Preferences.vue';
import ConnectedApplications from './components/ConnectedApplications.vue';

// component constants
const { t } = useI18n({ useScope: 'global' });
const route = useRoute();
const router = useRouter();
const sections = ref(enumToObject(SettingsSections));
// Note: Use direct variables in computed, otherwise it won't be updated if transformed (like by typing)
const activeView = computed<number>(() => (route.hash && sections.value[route.hash.slice(1) as string] ? sections.value[route.hash.slice(1) as string] : SettingsSections.AccountSettings));
const user = useUserStore();

// menu navigation of different views
const show = (key: string) => {
  router.push({ name: route.name, hash: `#${key}` });
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
    router.replace({ name: 'settings', hash: `#accountSettings` });
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
  <header>
    <h2>{{ t('label.settings') }}</h2>
  </header>

  <div class="main-container">
    <!-- sidebar navigation -->
    <aside>
      <button
        v-for="(view, key) in sections"
        :key="key"
        :class="{ 'active': view === activeView }"
        @click="show(key)"
        :data-testid="'settings-' + key + '-settings-btn'"
      >
        <span>{{ t('label.' + key) }}</span>
        <icon-chevron-right size="18" />
      </button>
    </aside>

    <!-- content -->
    <div class="page-content">
      <section id="accountSettings">
        <account-settings />
      </section>

      <section id="preferences">
        <preferences />
      </section>

      <section id="connectedApplications">
        <connected-applications />
      </section>
    </div>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

header {
  h2 {
    font-size: 2.25rem;
    font-weight: 300;
    margin-block-end: 2rem;
  }
}

section {
  border: 1px solid var(--colour-neutral-border);
  border-radius: 8px;
  padding: 1.5rem;
  align-self: flex-start;
  background-color: var(--colour-neutral-lower);
  margin-block-end: 2rem;
}

.main-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;

  aside {
    display: flex;
    flex-direction: column;
    gap: 1rem;

    button {
      display: flex;
      justify-content: space-between;
      padding: 1.25rem;
      border-radius: 12px;

      /* TODO: Update colors once final UI is ready */
      background-color: #4b5563;
      color: var(--colour-ti-base);

      &.active {
        background-color: var(--colour-apmt-primary-pressed);
      }

      &:hover {
        background-color: var(--colour-apmt-primary-hover);
      }
    }
  }
}

@media (--md) {
  .main-container {
    display: flex;
    flex-direction: row;
    gap: 2rem;

    aside {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      width: 320px;

      button {
        display: flex;
        align-items: center;
        text-align: start;
      }
    }

    .page-content {
      flex-grow: 1;
    }
  }
}
</style>