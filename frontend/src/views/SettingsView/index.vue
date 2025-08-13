<script setup lang="ts">
import {
  computed, inject, onMounted, ref, watch,
} from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { SettingsSections, AlertSchemes, ColourSchemes } from '@/definitions';
import { enumToObject } from '@/utils';
import { callKey } from '@/keys';
import { Alert, SubscriberResponse } from '@/models';
import { PrimaryButton, LinkButton } from '@thunderbirdops/services-ui';
import AlertBox from '@/elements/AlertBox.vue';
import { useUserStore } from '@/stores/user-store';
import { createSettingsStore } from '@/stores/settings-store';
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
const savingInProgress = ref(false);
const validationError = ref<Alert>(null);
const saveSuccess = ref<Alert>(null);

// Note: Use direct variables in computed, otherwise it won't be updated if transformed (like by typing)
const activeView = computed<number>(() => (route.hash && sections.value[route.hash.slice(1) as string] ? sections.value[route.hash.slice(1) as string] : SettingsSections.AccountSettings));
const userStore = useUserStore();

const call = inject(callKey);
const settingsStore = createSettingsStore(call);
const { currentState, isDirty } = storeToRefs(settingsStore)

const scrollToSection = (key: string) => {
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

async function onSaveChanges() {
  savingInProgress.value = true;

  const obj = {
    username: userStore.data.username,
    language: currentState.value.language,
    timezone: userStore.data.settings.timezone,
    colour_scheme: currentState.value.colourScheme,
    time_mode: currentState.value.timeFormat,
    start_of_week: currentState.value.startOfWeek,
  };

  switch (currentState.value.colourScheme) {
    case ColourSchemes.Dark:
      document.documentElement.classList.add('dark');
      break;
    case ColourSchemes.Light:
      document.documentElement.classList.remove('dark');
      break;
    case ColourSchemes.System:
      if (!window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.documentElement.classList.remove('dark');
      } else {
        document.documentElement.classList.add('dark');
      }
      break;
    default:
      break;
  }

  const { error }: SubscriberResponse = await call('me').put(obj).json();

  if (error.value) {
    validationError.value = { title: (error.value as unknown as Error).message };
    window.scrollTo(0, 0);
    return;
  }

  // Reload data form backend to reset currentState vs initialState
  settingsStore.$reset();

  saveSuccess.value = { title: t('info.settingsSavedSuccessfully') };
  window.scrollTo(0, 0);
}

function onRevertChanges() {
  settingsStore.revertChanges();
}

onMounted(() => {
  if (!userStore?.data.isSetup) {
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

  <alert-box
    class="alert-box"
    v-if="validationError"
    :alert="validationError"
    @close="validationError = null"
  />

  <alert-box
    class="alert-box"
    v-else-if="saveSuccess"
    :alert="saveSuccess"
    :scheme="AlertSchemes.Success"
    @close="saveSuccess = null"
  />

  <div class="main-container">
    <!-- sidebar navigation -->
    <aside>
      <button
        v-for="(view, key) in sections"
        :key="key"
        :class="{ 'active': view === activeView }"
        @click="scrollToSection(key)"
        :data-testid="'settings-' + key + '-settings-btn'"
      >
        <span>{{ t('label.' + key) }}</span>
        <icon-chevron-right size="18" />
      </button>
    </aside>

    <!-- content -->
    <div class="page-content" :class="{ 'is-dirty': isDirty }">
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

  <div class="footer-save-panel" v-if="isDirty">
    <link-button
      @click="onRevertChanges"
      :disabled="savingInProgress"
    >
      {{ t('label.revertChanges') }}
    </link-button>
    <primary-button
      @click="onSaveChanges"
      :disabled="savingInProgress"
    >
      {{ t('label.saveChanges') }}
    </primary-button>
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

.alert-box {
  margin-block-end: 2rem;
}

.main-container {
  position: relative;
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
      background-color: var(--colour-neutral-lower);

      &.active {
        color: var(--colour-neutral-lower);
        background-color: var(--colour-apmt-primary-pressed);
      }

      &:hover {
        background-color: var(--colour-apmt-primary-hover);
      }
    }
  }

  .page-content.is-dirty {
    margin-block-end: 4rem;
  }
}

.footer-save-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: flex-end;
  gap: 2rem;
  margin-inline-start: auto;
  padding: 1rem 1.5rem;
  margin: 0 0.5rem 0.5rem 0.5rem;
  border-radius: 8px;
  background-color: var(--colour-neutral-lower);
  z-index: 99;
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