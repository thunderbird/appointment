<script setup lang="ts">
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { PhDotsThree } from '@phosphor-icons/vue';
import { PrimaryButton, BaseBadge, CheckboxInput } from '@thunderbirdops/services-ui';
import { storeToRefs } from 'pinia';
import { CalendarProviders, ExternalConnectionProviders } from '@/definitions';
import DropDown from '@/elements/DropDown.vue';
import GenericModal from '@/components/GenericModal.vue';
import CalDavProvider from '@/components/CalDavProvider.vue';
import ConfirmationModal from '@/components/ConfirmationModal.vue';
import { keyByValue } from '@/utils';
import { Alert, ExternalConnection, HTMLInputElementEvent } from '@/models';
import { useExternalConnectionsStore } from '@/stores/external-connections-store';
import { useSettingsStore } from '@/stores/settings-store';
import { useCalendarStore } from '@/stores/calendar-store';
import { useUserStore } from '@/stores/user-store';
import { useAvailabilityStore } from '@/stores/availability-store';

const { t } = useI18n();

const videoMeetingDropdown = ref();
const calDavErrorMessage = ref();
const calendarDropdownRefs = ref({});
const disconnectTypeId = ref(null);
const disconnectConnectionName = ref(null);

// Modals
const connectCalDavModalOpen = ref(false);
const disconnectCalDavModalOpen = ref(false);
const disconnectZoomModalOpen = ref(false);
const disconnectGoogleModalOpen = ref(false);

const userStore = useUserStore();
const externalConnectionStore = useExternalConnectionsStore();
const calendarStore = useCalendarStore();
const settingsStore = useSettingsStore();
const availabilityStore = useAvailabilityStore();

const { currentState } = storeToRefs(settingsStore);
const { calendars } = storeToRefs(calendarStore);

const zoomAccount = computed(() => externalConnectionStore.zoom[0]);

// This computed property refers to the calendars from the backend combined
// with some data from external connections to facilitate connection / disconnection.
// It should be immutable as it represents the current state of the backend data.
const initialCalendars = computed(() => {
  const formattedCalendars = calendars.value?.map((calendar) => {
    const connectionProvider = keyByValue(CalendarProviders, calendar.provider, true);
    const externalConnection: ExternalConnection = externalConnectionStore
      .connections[connectionProvider]
      .find((ec: ExternalConnection) => ec.id === calendar.external_connection_id)

    // Injecting type_id and connection_name from externalConnectionStore
    // to facilitate the disconnection logic
    return {
      ...calendar,
      type_id: externalConnection?.type_id,
      connection_name: externalConnection?.name,
      provider_name: connectionProvider,
      is_default: currentState.value.defaultCalendarId === calendar.id,
    }
  }) || [];

  const sortedCalendars = formattedCalendars.sort((a, b) => a.title.localeCompare(b.title));

  return sortedCalendars;
});

async function connectGoogleCalendar() {
  await calendarStore.connectGoogleCalendar();
}

async function afterCalDavConnect() {
  connectCalDavModalOpen.value = false;
  externalConnectionStore.$reset();
  await refreshData();
}

async function disconnectAccount(provider: ExternalConnectionProviders, typeId: string | null = null) {
  await externalConnectionStore.disconnect(provider, typeId);
  closeModals();
  externalConnectionStore.$reset();
  await refreshData();
}

function displayModal(
  provider: ExternalConnectionProviders | CalendarProviders,
  typeId: string | null = null,
  connectionName: string | null = null,
  isCalendar: boolean = false,
) {
  disconnectTypeId.value = typeId;
  disconnectConnectionName.value = connectionName;

  if (isCalendar) {
    if (provider === CalendarProviders.Google) {
      disconnectGoogleModalOpen.value = true;
    } else if (provider === CalendarProviders.Caldav) {
      disconnectCalDavModalOpen.value = true;
    }
  } else {
    if (provider === ExternalConnectionProviders.Zoom) {
      disconnectZoomModalOpen.value = true;
    }
  }
};

function closeModals() {
  connectCalDavModalOpen.value = false;
  disconnectZoomModalOpen.value = false;
  disconnectGoogleModalOpen.value = false;
  disconnectCalDavModalOpen.value = false;
  disconnectTypeId.value = null;
  disconnectConnectionName.value = null;
}

function onCalendarChecked(event: HTMLInputElementEvent, calendarId: number) {
  // Only update local state, the actual connection / disconnection
  // of the calendar happens on save changes in SettingsView/index.vue
  settingsStore.$patch({
    currentState: {
      changedCalendars: {
        ...currentState.value.changedCalendars,
        [calendarId]: event.target.checked
      }
    }
  })
}

function onSetAsDefaultClicked(calendarId: number) {
  // Only update local state, the actual schedule's calendar change
  // happens on save changes in SettingsView/index.vue
  settingsStore.$patch({ currentState: { defaultCalendarId: calendarId }});
  // Update the current availability too, otherwise it will be out
  // of sync until the user refreshes the page
  availabilityStore.$patch({
    initialState: { calendar_id: calendarId },
    currentState: { calendar_id: calendarId },
  });
}

function onCalendarColorChanged(event: HTMLInputElementEvent, calendarId: number) {
  // Only update local state, the actual calendar color change
  // happens on save changes in SettingsView/index.vue
  settingsStore.$patch({
    currentState: {
      changedCalendarColors: {
        ...currentState.value.changedCalendarColors,
        [calendarId]: event.target.value
      }
    }
  })
}

async function refreshData() {
  // Need to reset calendar store first!
  calendarStore.$reset();

  await Promise.all([
    settingsStore.$reset(),
    externalConnectionStore.fetch(true),
    calendarStore.fetch(),
    // Need to update userStore in case they used an attached email
    userStore.profile(),
  ]);
};
</script>

<template>
  <header>
    <h2>{{ t('heading.connectedApplications') }}</h2>
  </header>

  <div class="form-field-container">
    <!-- Video Meeting -->
    <label class="form-field-label" for="videoMeeting">
      {{ t('label.videoMeeting') }}
    </label>

    <template v-if="zoomAccount">
      <p>{{ t('label.connectedAs', { name: zoomAccount.name }) }}</p>
      <br />
      <p>{{ t('heading.zoom') }}</p>

      <drop-down class="dropdown" ref="videoMeetingDropdown">
        <template #trigger>
          <ph-dots-three size="24" />
        </template>
        <template #default>
          <div class="dropdown-inner" @click="videoMeetingDropdown.close()">
            <button @click="() => displayModal(ExternalConnectionProviders.Zoom, zoomAccount.type_id)">
              {{ t('label.disconnect') }}
            </button>
          </div>
        </template>
      </drop-down>
    </template>

    <template v-else>
      <i18n-t keypath="text.generateZoomMeetingHelpDisabled.text" tag="p" scope="global" class="video-not-connected">
        <template v-slot:link>
          <button @click="settingsStore.connectZoom">
            {{ t('text.generateZoomMeetingHelpDisabled.link') }}
          </button>
        </template>
      </i18n-t>
    </template>

    <!-- Calendars -->
    <label class="form-field-label" for="calendars">
      {{ t('label.calendar', initialCalendars.length) }}
    </label>

    <template v-if="initialCalendars.length > 0">
      <template v-for="calendar in initialCalendars" :key="calendar.id">
        <div class="calendar-details-container">
          <checkbox-input
            :name="`calendarConnected-${calendar.id}`"
            class="calendar-connected-checkbox"
            @change="(event) => onCalendarChecked(event, calendar.id)"
            :checked="currentState.changedCalendars?.[calendar.id] !== undefined ? currentState.changedCalendars[calendar.id] : calendar.connected"
            :disabled="calendar.is_default"
          />
          <base-badge v-if="calendar.is_default">
            {{ t('label.default') }}
          </base-badge>
          <p>{{ calendar.title }}</p>
        </div>
  
        <div class="calendar-color" :style="{ backgroundColor: calendar.color }">
          <input
            type="color"
            :value="calendar.color"
            @change="(event) => onCalendarColorChanged(event as HTMLInputElementEvent, calendar.id)"
          />
        </div>
  
        <p class="calendar-provider">{{ calendar.provider_name }}</p>
  
        <drop-down
          v-if="!calendar.is_default"
          class="dropdown"
          :ref="(el) => calendarDropdownRefs[calendar.id] = el"
        >
          <template #trigger>
            <icon-dots size="24" />
          </template>
          <template #default>
            <div class="dropdown-inner" @click="calendarDropdownRefs[calendar.id].close()">
              <button
                v-if="calendar.connected && !calendar.is_default"
                @click="() => onSetAsDefaultClicked(calendar.id)"
              >
                {{ t('text.settings.connectedApplications.setAsDefault') }}
              </button>
              <!-- TODO: Rename Calendar not implemented -->
              <!-- <button>
                {{ t('text.settings.connectedApplications.renameCalendar') }}
              </button> -->
              <button
                @click="() => displayModal(calendar.provider, calendar.type_id, calendar.connection_name, true)"
                :disabled="calendar.is_default"
              >
                {{ t('label.disconnect') }}
              </button>
            </div>
          </template>
        </drop-down>
        <span v-else></span>
        <span></span>
      </template>
    </template>

    <template v-else>
      <p class="calendar-accounts-not-connected">{{ t('text.settings.calendars.noCalendars') }}</p>
    </template>
  </div>

  <div class="footer-buttons-container">
    <primary-button variant="outline" @click="connectGoogleCalendar">
      {{ t('label.addGoogleCalendar') }}
    </primary-button>
    <primary-button variant="outline" @click="connectCalDavModalOpen = true">
      {{ t('label.addCalDavCalendar') }}
    </primary-button>
  </div>

  <!-- Connect CalDav Modal Flow -->
  <generic-modal v-if="connectCalDavModalOpen" @close="connectCalDavModalOpen = false"
    :error-message="calDavErrorMessage">
    <template v-slot:header>
      <h2 class="modal-title">
        {{ t('heading.settings.connectedApplications.caldav') }}
      </h2>
    </template>
    <cal-dav-provider @next="afterCalDavConnect()" @error="(alert: Alert) => calDavErrorMessage = alert" />
  </generic-modal>

  <!-- Disconnect Google Modal -->
  <confirmation-modal :open="disconnectGoogleModalOpen"
    :title="t('text.settings.connectedApplications.disconnect.google.title')"
    :message="t('text.settings.connectedApplications.disconnect.google.message', { googleAccountName: disconnectConnectionName })"
    :confirm-label="t('text.settings.connectedApplications.disconnect.google.confirm')"
    :cancel-label="t('text.settings.connectedApplications.disconnect.google.cancel')" :use-caution-button="true"
    @confirm="() => disconnectAccount(ExternalConnectionProviders.Google, disconnectTypeId)" @close="closeModals" />
  <!-- Disconnect CalDav Modal -->
  <confirmation-modal :open="disconnectCalDavModalOpen"
    :title="t('text.settings.connectedApplications.disconnect.caldav.title')"
    :message="t('text.settings.connectedApplications.disconnect.caldav.message')"
    :confirm-label="t('text.settings.connectedApplications.disconnect.caldav.confirm')"
    :cancel-label="t('text.settings.connectedApplications.disconnect.caldav.cancel')" :use-caution-button="true"
    @confirm="() => disconnectAccount(ExternalConnectionProviders.Caldav, disconnectTypeId)" @close="closeModals" />
  <!-- Disconnect Zoom Modal -->
  <confirmation-modal :open="disconnectZoomModalOpen"
    :title="t('text.settings.connectedApplications.disconnect.zoom.title')"
    :message="t('text.settings.connectedApplications.disconnect.zoom.message')"
    :confirm-label="t('text.settings.connectedApplications.disconnect.zoom.confirm')"
    :cancel-label="t('text.settings.connectedApplications.disconnect.zoom.cancel')" :use-caution-button="true"
    @confirm="() => disconnectAccount(ExternalConnectionProviders.Zoom, zoomAccount.type_id)"
    @close="disconnectZoomModalOpen = false"></confirmation-modal>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

header {
  margin-block-end: 2rem;
}

h2 {
  color: var(--colour-ti-highlight);
  font-size: 1.5rem;
}

.form-field-container {
  display: grid;
  align-items: center;
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

  .calendar-accounts-not-connected {
    grid-column: span 4;
  }

  .calendar-provider {
    text-transform: capitalize;
  }

  .dropdown {
    position: initial;

    .dropdown-inner {
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.5rem;
      padding: 0.5rem;
      min-width: max-content;
      background-color: var(--colour-neutral-base);
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
      z-index: 2;

      button {
        width: 100%;
        padding: 0.5rem;

        &:hover {
          background-color: var(--colour-neutral-lower);
        }
      }
    }
  }
}

.calendar-details-container {
  display: flex;
  align-items: center;
  gap: 1.5rem;

  .checkbox-wrapper {
     width: auto;
  }

  .calendar-connected-checkbox {
    width: auto;
  }
}

.calendar-color {
  width: 24px;
  height: 24px;

  input {
    width: 24px;
    height: 24px;
    border: none;
    cursor: pointer;

    &::-moz-color-swatch {
      border: none;
    }

    &::-webkit-color-swatch {
      border: none;
    }
  }
}

.modal-title {
  color: var(--colour-ti-base);
  font-weight: 400;
  font-size: 1.375rem;
  line-height: 1.664rem;
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
