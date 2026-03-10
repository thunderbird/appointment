<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';
import { PhDotsThree, PhWarningCircle } from '@phosphor-icons/vue';
import { PrimaryButton, BaseBadge, CheckboxInput, BaseBadgeTypes } from '@thunderbirdops/services-ui';
import { storeToRefs } from 'pinia';
import { CalendarProviders, ExternalConnectionProviders, ProviderDisplayName } from '@/definitions';
import DropDown from '@/elements/DropDown.vue';
import ConfirmationModal from '@/components/ConfirmationModal.vue';
import CaldavConnectModal from './CaldavConnectModal.vue';
import { ExternalConnection, ExternalConnectionStatus, HTMLInputElementEvent } from '@/models';
import { useExternalConnectionsStore } from '@/stores/external-connections-store';
import { useSettingsStore } from '@/stores/settings-store';
import { useCalendarStore } from '@/stores/calendar-store';
import { useUserStore } from '@/stores/user-store';
import { useAvailabilityStore } from '@/stores/availability-store';

const { t } = useI18n();

const videoMeetingDropdown = ref();
const calendarDropdownRefs = ref({});
const connectionDropdownRefs = ref({});
const disconnectTypeId = ref(null);
const disconnectConnectionName = ref(null);

// Modals
const connectCaldavModal = useTemplateRef('connectCaldavModal');
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

const calendarConnectedMap = new Map<number, ReturnType<typeof computed<boolean>>>();

const zoomAccount = computed(() => externalConnectionStore.zoom[0]);

// Calendars from the backend, enriched with external connection data and
// grouped by external connection for display purposes.
// Should be treated as immutable since it represents the current backend state.
const groupedCalendars = computed(() => {
  const defaultCalendar = calendars.value?.find(
    (calendar) => calendar.id === currentState.value.defaultCalendarId
  );
  const defaultExternalConnectionId = defaultCalendar?.external_connection_id;

  const calendarProviders = [
    ['google', CalendarProviders.Google],
    ['caldav', CalendarProviders.Caldav],
  ];

  return calendarProviders.flatMap(([providerKey, provider]) => {
    const connections = externalConnectionStore.connections[providerKey] ?? [];
    const providerName = ProviderDisplayName[providerKey] ?? providerKey;

    return connections.map((connection: ExternalConnection) => ({
      connectionId: connection.id,
      connectionName: connection.name ?? '',
      connectionStatus: connection.status,
      providerName,
      provider,
      typeId: connection.type_id,
      sharesDefaultConnection: connection.id === defaultExternalConnectionId,
      calendars: (calendars.value ?? [])
        .filter((cal) => cal.external_connection_id === connection.id)
        .sort((a, b) => a.title.localeCompare(b.title)),
    }));
  }).filter((group) => group.calendars.length > 0);
});

const calendarCount = computed(() =>
  groupedCalendars.value.reduce((sum, group) => sum + group.calendars.length, 0)
);

async function connectGoogleCalendar() {
  await calendarStore.connectGoogleCalendar();
}

async function disconnectAccount(provider: ExternalConnectionProviders, typeId: string | null = null) {
  await externalConnectionStore.disconnect(provider, typeId);
  closeModals();
  externalConnectionStore.$reset();
  await refreshData();
}

function displayDisconnectModal(
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
  connectCaldavModal.value.hide();
  disconnectZoomModalOpen.value = false;
  disconnectGoogleModalOpen.value = false;
  disconnectCalDavModalOpen.value = false;
  disconnectTypeId.value = null;
  disconnectConnectionName.value = null;
}

function calendarConnected(calendarId: number) {
  if (!calendarConnectedMap.has(calendarId)) {
    calendarConnectedMap.set(calendarId, computed({
      get: () => {
        const calendar = groupedCalendars.value.flatMap(g => g.calendars).find(c => c.id === calendarId);
        return currentState.value.changedCalendars?.[calendarId] !== undefined
          ? currentState.value.changedCalendars[calendarId]
          : calendar?.connected ?? false;
      },
      set: (value: boolean) => {
        const calendar = groupedCalendars.value.flatMap(g => g.calendars).find(c => c.id === calendarId);
        const originalValue = calendar?.connected ?? false;
        settingsStore.updateCalendarConnected(calendarId, value, originalValue);
      }
    }));
  }

  return calendarConnectedMap.get(calendarId)!;
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

function reconnectExternalConnection(provider: ExternalConnectionProviders | CalendarProviders, isCalendar: boolean = false) {
  if (isCalendar) {
    if (provider === CalendarProviders.Google) {
      connectGoogleCalendar();
    } else if (provider === CalendarProviders.Caldav) {
      connectCaldavModal.value.show();
    }

    return;
  }

  if (provider === ExternalConnectionProviders.Zoom) {
    settingsStore.connectZoom();
  }
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

onMounted(async () => {
  await externalConnectionStore.checkStatus();
})
</script>

<template>
  <header>
    <h2>{{ t('heading.connectedApplications') }}</h2>
  </header>

  <div class="form-field-container">
    <div>
      <!-- Video Meeting -->
      <label for="videoMeeting" class="video-label">
        {{ t('label.videoMeeting') }}
      </label>
  
      <hr class="divider" />

      <template v-if="zoomAccount">
        <div class="video-meeting-container">
          <template v-if="zoomAccount.status === ExternalConnectionStatus.error">
            <p class="connection-error-message zoom-error-message">
              <ph-warning-circle weight="fill" size="24" />
              <i18n-t keypath="text.settings.connectedApplications.connectionUnreachableZoom" tag="span">
                <template v-slot:email>
                  <strong>{{ zoomAccount.name }}</strong>
                </template>
              </i18n-t>
            </p>
          </template>
          <template v-else>
            <p class="connection-name">{{ zoomAccount.name }}</p>
          </template>

          <img src="@/assets/images/zoom-mini-logo.png" alt="Zoom" />
          <p class="connection-provider">{{ t('heading.zoom') }}</p>

          <drop-down class="dropdown" ref="videoMeetingDropdown">
            <template #trigger>
              <ph-dots-three size="24" />
            </template>
            <template #default>
              <div class="dropdown-inner" @click="videoMeetingDropdown.close()">
                <button
                  v-if="zoomAccount.status === ExternalConnectionStatus.error"
                  @click="reconnectExternalConnection(ExternalConnectionProviders.Zoom)"
                >
                  {{ t('label.reconnect') }}
                </button>
                <button @click="() => displayDisconnectModal(ExternalConnectionProviders.Zoom, zoomAccount.type_id)">
                  {{ t('label.remove') }}
                </button>
              </div>
            </template>
          </drop-down>
        </div>
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
    </div>

    <!-- Calendars -->
    <div>
      <label for="calendars" class="calendars-label">
        {{ t('label.calendar', calendarCount) }}
      </label>
  
      <hr class="divider" />

      <template v-if="groupedCalendars.length > 0">
        <template v-for="(group, groupIndex) in groupedCalendars" :key="group.connectionId">
          <hr v-if="groupIndex > 0" class="divider" />

          <div class="calendars-container">
            <!-- Connection header row -->
            <p class="connection-name">{{ group.connectionName }}</p>
            <span />
            <p class="connection-provider">{{ group.providerName }}</p>
            <drop-down
              class="dropdown"
              :ref="(el) => connectionDropdownRefs[group.connectionId] = el"
            >
              <template #trigger>
                <ph-dots-three size="24" />
              </template>
              <template #default>
                <div class="dropdown-inner" @click="connectionDropdownRefs[group.connectionId]?.close()">
                  <button
                    @click="reconnectExternalConnection(group.provider, true)"
                  >
                    {{ t('label.reconnect') }}
                  </button>
                  <button
                    v-if="!group.sharesDefaultConnection"
                    @click="() => displayDisconnectModal(group.provider, group.typeId, group.connectionName, true)"
                  >
                    {{ t('label.remove') }}
                  </button>
                </div>
              </template>
            </drop-down>

            <!-- Calendar rows -->

            <!-- If there's a connection error, don't display any calendars, instead display the error message -->
            <template v-if="group.connectionStatus === ExternalConnectionStatus.error">
              <p class="connection-error-message">
                <ph-warning-circle weight="fill" size="24" />

                <template v-if="group.sharesDefaultConnection">
                  {{ t('text.settings.connectedApplications.connectionUnreachableDefault', { providerName: group.providerName }) }}
                </template>
                <template v-else>
                  {{ t('text.settings.connectedApplications.connectionUnreachableNonDefault', { providerName: group.providerName }) }}
                </template>
              </p>
            </template>

            <template v-else v-for="calendar in group.calendars" :key="calendar.id">
              <checkbox-input
                :name="`calendarConnected-${calendar.id}`"
                class="calendar-connected-checkbox"
                v-model="calendarConnected(calendar.id).value"
                v-bind="calendar.id === currentState.defaultCalendarId ? { disabled: true } : {}"
                :label="calendar.title"
              />

              <template v-if="calendar.id === currentState.defaultCalendarId">
                <base-badge :type="BaseBadgeTypes.Default">
                  {{ t('label.default') }}
                </base-badge>
              </template>
              <template v-else>
                <span />
              </template>

              <div class="calendar-color" :style="{ backgroundColor: calendar.color }">
                <input
                  type="color"
                  :value="calendar.color"
                  @change="(event) => onCalendarColorChanged(event as HTMLInputElementEvent, calendar.id)"
                />
              </div>

              <p>{{ group.providerName }}</p>

              <drop-down
                class="dropdown"
                :ref="(el) => calendarDropdownRefs[calendar.id] = el"
              >
                <template #trigger>
                  <ph-dots-three size="24" />
                </template>
                <template #default>
                  <div class="dropdown-inner" @click="calendarDropdownRefs[calendar.id]?.close()">
                    <button
                      v-if="calendar.connected && calendar.id !== currentState.defaultCalendarId"
                      @click="() => onSetAsDefaultClicked(calendar.id)"
                    >
                      {{ t('text.settings.connectedApplications.setAsDefault') }}
                    </button>
                    <button
                      @click="() => displayDisconnectModal(group.provider, group.typeId, group.connectionName, true)"
                    >
                      {{ t('label.remove') }}
                    </button>
                  </div>
                </template>
              </drop-down>
            </template>
          </div>
        </template>
      </template>

      <template v-else>
        <p class="calendar-accounts-not-connected">{{ t('text.settings.calendars.noCalendars') }}</p>
      </template>
    </div>
  </div>

  <div class="footer-buttons-container">
    <primary-button variant="outline" size="small" @click="connectGoogleCalendar">
      {{ t('label.addGoogleCalendar') }}
    </primary-button>
    <primary-button variant="outline" size="small" @click="connectCaldavModal.show()">
      {{ t('label.addCalDavCalendar') }}
    </primary-button>
  </div>

  <!-- Connect CalDav Modal Flow -->
  <caldav-connect-modal ref="connectCaldavModal" @connected="refreshData" />

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
  margin-block-end: 1.5rem;
}

h2 {
  color: var(--colour-ti-highlight);
  font-size: 1.5rem;
  font-family: metropolis;
}

.divider {
  color: var(--colour-neutral-border);
  height: 1px;
  margin-block: 0.5rem;
}

.form-field-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-block-end: 2rem;

  .calendars-label, .video-label {
    display: block;
    color: var(--colour-ti-secondary);
    letter-spacing: 0.48px;
    font-weight: 500;
  }

  .connection-provider {
    font-weight: 500; 
  }

  .video-meeting-container {
    display: grid;
    grid-template-columns: 1fr 26px auto 24px;
    grid-gap: 1rem;
    align-items: center;
    overflow-x: auto;

    img {
      width: 20px;
    }

    .connection-name {
      font-weight: 600;
      color: var(--colour-ti-base);
    }
  }

  .calendars-container {
    display: grid;
    grid-template-columns: auto 1fr min-content 12px auto 24px;
    grid-row-gap: 0.5rem;
    grid-column-gap: 1rem;
    align-items: center;
    overflow-x: auto;
    padding-block-end: 0.5rem;

    .calendar-connected-checkbox {
      grid-column: 1 / 3;
      font-size: 0.875rem;
    }

    .connection-name {
      grid-column: 1 / 4;
      font-weight: 500;
      color: var(--colour-ti-base);
      margin-block-end: 0.125rem;
    }
  }

  .video-not-connected {
    grid-column: span 4;

    button {
      text-decoration: underline;
      color: var(--colour-primary-default);
    }
  }

  .calendar-accounts-not-connected {
    grid-column: span 4;
  }

  .connection-error-message {
    grid-column: 1 / 4;
    display: flex;
    align-items: start;
    gap: 0.5rem;
    color: var(--colour-ti-base);

    svg {
      margin-top: 0.125rem;
      flex-shrink: 0;
      color: var(--colour-danger-default);
    }

    &.zoom-error-message {
      grid-column: 1 / 2;
    }
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
        text-align: start;

        &:hover {
          background-color: var(--colour-neutral-lower);
        }
      }
    }
  }
}

.calendar-color {
  position: relative;
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 9999px;

  input {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: none;
    cursor: pointer;
    border-radius: 9999px;

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
