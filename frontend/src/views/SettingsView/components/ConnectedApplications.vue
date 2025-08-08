<script setup lang="ts">
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { IconDots } from '@tabler/icons-vue';
import { CheckboxInput, SecondaryButton } from '@thunderbirdops/services-ui';
import { CalendarProviders } from '@/definitions';
import DropDown from '@/elements/DropDown.vue';
import GenericModal from '@/components/GenericModal.vue';
import CalDavProvider from '@/components/FTUE/CalDavProvider.vue';
import { keyByValue } from '@/utils';
import { Alert } from '@/models';
import { useExternalConnectionsStore } from '@/stores/external-connections-store';
import { useSettingsStore } from '@/stores/settings-store';
import { useCalendarStore } from '@/stores/calendar-store';
import { useUserStore } from '@/stores/user-store';

const { t } = useI18n();
const calendarDropdown = ref();
const connectCalDavModalOpen = ref(false);
const calDavErrorMessage = ref();

const userStore = useUserStore();
const externalConnectionStore = useExternalConnectionsStore();
const calendarStore = useCalendarStore();
const settingsStore = useSettingsStore();

const hasZoomAccount = computed(() => externalConnectionStore.zoom[0]);
const calendars = computed(() => calendarStore.calendars);

async function connectGoogleCalendar() {
  await calendarStore.connectGoogleCalendar(userStore.data.email);
}

function afterCalDavConnect() {
  connectCalDavModalOpen.value = false;
}
</script>

<template>
  <header>
    <h2>{{ t('label.connectedApplications') }}</h2>
  </header>

  <div class="form-field-container">
    <!-- Video Meeting -->
    <label class="form-field-label" for="videoMeeting">
      {{ t('label.videoMeeting') }}
    </label>

    <template v-if="hasZoomAccount">
      <p>Connected as dnakano@email.com</p>
      <br />
      <p>Zoom</p>
      <icon-dots size="24" />
    </template>

    <template v-else>
      <i18n-t
        keypath="text.generateZoomMeetingHelpDisabled.text"
        tag="p"
        scope="global"
        class="video-not-connected"
      >
        <template v-slot:link>
          <button @click="settingsStore.connectZoom">
            {{ t('text.generateZoomMeetingHelpDisabled.link') }}
          </button>
        </template>
      </i18n-t>
    </template>

    <!-- Calendars -->
    <label class="form-field-label" for="calendars">
      {{ t('label.calendar', calendars.length) }}
    </label>

    <template
      v-for="calendar in calendars"
      :key="calendar.id"
    >
      <div class="calendar-details-container">
        <checkbox-input
          name="calendarConnected"
          class="calendar-connected-checkbox"
          v-model="calendar.connected"
        />
        <!-- TODO: How do we know which calendar is the default? -->
        <!-- <primary-badge>
          {{ t('label.default') }}
        </primary-badge> -->
        <p>{{ calendar.title }}</p>
      </div>
  
      <div class="calendar-color" :style="{ backgroundColor: calendar.color }"></div>

      <p class="calendar-provider">{{ keyByValue(CalendarProviders, calendar.provider, true) }}</p>
  
      <drop-down class="self-center" ref="calendarDropdown">
        <template #trigger>
          <icon-dots size="24" />
        </template>
        <template #default>
          <div @click="calendarDropdown.close()">
            <p>hey</p>
          </div>
        </template>
      </drop-down>

      <br />
    </template>
  </div>

  <div class="footer-buttons-container">
    <secondary-button @click="connectGoogleCalendar">
      {{ t('label.addGoogleCalendar') }}
    </secondary-button>
    <secondary-button @click="connectCalDavModalOpen = true">
      {{ t('label.addCalDavCalendar') }}
    </secondary-button>
  </div>

  <!-- Connect CalDav Modal Flow -->
  <generic-modal v-if="connectCalDavModalOpen" @close="connectCalDavModalOpen = false" :error-message="calDavErrorMessage">
    <template v-slot:header>
      <h2 class="modal-title">
        {{ t('heading.settings.connectedAccounts.caldav') }}
      </h2>
    </template>
    <cal-dav-provider @next="afterCalDavConnect()" @error="(alert: Alert) => calDavErrorMessage = alert" />
  </generic-modal>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

header {
  margin-block-end: 2rem;
}

h2 {
  font-size: 1.5rem;
}

.form-field-container {
  display: grid;
  grid-template-columns: 20% 2fr 24px 1fr 24px;
  grid-gap: 1.5rem;
  margin-block-end: 2rem;
  overflow-x: auto;

  .video-not-connected {
    grid-column: span 4;

    button {
      text-decoration: underline;
      color: var(--colour-apmt-primary);
    }
  }

  .calendar-provider {
    text-transform: capitalize;
  }
}

.calendar-details-container {
  display: flex;
  align-items: center;
  gap: 1.5rem;

  .calendar-connected-checkbox {
    width: auto;
  }
}

.calendar-color {
  width: 24px;
  height: 24px;
}

.footer-buttons-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  gap: 1rem;

  button {
    width: 100%;
  }
}

@media (--md) {
  .footer-buttons-container {
    flex-direction: row;

    button {
      width: auto;
    }
  }
}
</style>