<script setup lang="ts">
import { CalendarManagementType, CalendarProviders, MetricEvents } from '@/definitions';
import { IconArrowRight } from '@tabler/icons-vue';
import {
  ref, reactive, inject, onMounted, computed,
} from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { useCalendarStore } from '@/stores/calendar-store';
import { callKey, refreshKey } from '@/keys';
import {
  Calendar, CalendarResponse, CalendarListResponse, Exception, ExceptionDetail,
} from '@/models';
import AlertBox from '@/elements/AlertBox.vue';
import CalendarManagement from '@/components/CalendarManagement.vue';
import CautionButton from '@/elements/CautionButton.vue';
import ConfirmationModal from '@/components/ConfirmationModal.vue';
import GoogleCalendarButton from '@/elements/GoogleCalendarButton.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import SecondaryButton from '@/elements/SecondaryButton.vue';
import { posthog, usePosthog } from '@/composables/posthog';

// component constants
const { t } = useI18n({ useScope: 'global' });
const call = inject(callKey);
const refresh = inject(refreshKey);
const calendarStore = useCalendarStore();

const calendarConnectError = ref('');

const deleteCalendarModalOpen = ref(false);
const deleteCalendarModalTarget = ref<number>(null);

// Temp until we get a store solution rolling
const loading = ref(false);

// handle calendar user input to add or edit calendar connections
enum InputModes {
  Hidden,
  Add,
  Edit,
}
const inputMode = ref(InputModes.Hidden);
const addMode = computed(() => inputMode.value === InputModes.Add);
const editMode = computed(() => inputMode.value === InputModes.Edit);

// supported calendar providers
const defaultCalendarInput = {
  provider: CalendarProviders.Caldav,
  title: '',
  color: '',
  url: '',
  user: '',
  password: '',
};
const calendarInput = reactive({
  id: null,
  data: { ...defaultCalendarInput },
});
const isCalDav = computed(() => calendarInput.data.provider === CalendarProviders.Caldav);
const isGoogle = computed(() => calendarInput.data.provider === CalendarProviders.Google);

const closeModals = async () => {
  deleteCalendarModalTarget.value = null;
  deleteCalendarModalOpen.value = false;
};

const refreshData = async () => {
  // Invalidate our calendar store
  calendarStore.$reset();
  await refresh();
  loading.value = false;
};

// clear input fields
const resetInput = () => {
  calendarInput.id = null;
  calendarInput.data = { ...defaultCalendarInput };
  inputMode.value = InputModes.Hidden;
  loading.value = false;
};

/**
 * Send off some metrics
 * @param event {MetricEvents}
 * @param properties {Object}
 */
const sendMetrics = (event, properties = {}) => {
  if (usePosthog) {
    posthog.capture(event, properties);
  }
};

// set input mode for adding or editing
const addCalendar = (provider: number) => {
  inputMode.value = InputModes.Add;
  calendarInput.data.provider = provider;
};
const connectCalendar = async (id: number) => {
  loading.value = true;

  await calendarStore.connectCalendar(call, id);
  await refreshData();
  resetInput();
  sendMetrics(MetricEvents.ConnectCalendar, { provider: calendarStore.calendarById(id)?.provider });
};
const disconnectCalendar = async (id: number) => {
  loading.value = true;

  await calendarStore.disconnectCalendar(call, id);
  await refreshData();
  resetInput();
  sendMetrics(MetricEvents.DisconnectCalendar, { provider: calendarStore.calendarById(id)?.provider });
};
const syncCalendars = async () => {
  loading.value = true;

  const oldCount = calendarStore?.calendars?.length ?? 0;

  await calendarStore.syncCalendars(call);
  await refreshData();

  const newCount = calendarStore?.calendars?.length ?? 0;

  sendMetrics(MetricEvents.DisconnectCalendar, { oldCount, newCount });
};
const editCalendar = async (id: number) => {
  loading.value = true;

  inputMode.value = InputModes.Edit;
  calendarInput.id = id;
  const { data }: CalendarResponse = await call(`cal/${id}`).get().json();
  Object.keys(data.value).forEach((attr) => {
    calendarInput.data[attr] = data.value[attr];
  });

  loading.value = false;
};

const deleteCalendar = async (id: number) => {
  deleteCalendarModalTarget.value = id;
  deleteCalendarModalOpen.value = true;
};

// do remove a given calendar connection
const deleteCalendarConfirm = async () => {
  loading.value = true;

  await call(`cal/${deleteCalendarModalTarget.value}`).delete();
  await refreshData();
  await closeModals();
};

// do save calendar data
const saveCalendar = async () => {
  loading.value = true;

  if (inputMode.value === InputModes.Add) {
    sendMetrics(MetricEvents.AddCalendar, { provider: calendarInput.data.provider });
  }

  // add new caldav calendar
  if (isCalDav.value && inputMode.value === InputModes.Add) {
    const { error, data }: CalendarResponse = await call('cal').post(calendarInput.data).json();
    if (error.value) {
      calendarConnectError.value = ((data.value as Exception)?.detail as ExceptionDetail)?.message;
      loading.value = false;
      // Show them the error message because I haven't thought this ux process through.
      window.scrollTo(0, 0);
      return;
    }
  }
  // add all google calendars connected to given gmail address
  if (isGoogle.value && inputMode.value === InputModes.Add) {
    await calendarStore.connectGoogleCalendar(call, calendarInput.data.user);
    return;
  }

  // edit existing calendar connection
  if (inputMode.value === InputModes.Edit) {
    await call(`cal/${calendarInput.id}`).put(calendarInput.data);
    sendMetrics(MetricEvents.EditCalendar, { provider: calendarInput.data.provider });
  }

  // refresh list of calendars
  await refreshData();
  resetInput();
};

// discover calendars by principal
const principal = reactive({
  url: '',
  user: '',
  password: '',
});
const processPrincipal = ref(false);
const searchResultCalendars = ref<Calendar[]>([]);
const getRemoteCalendars = async () => {
  processPrincipal.value = true;
  const { error, data }: CalendarListResponse = await call('rmt/calendars').post(principal).json();
  searchResultCalendars.value = !error.value ? data.value : [];
  processPrincipal.value = false;
};

// fill input form with data from principal discovery
const assignCalendar = (title: string, url: string) => {
  inputMode.value = InputModes.Add;
  calendarInput.data.title = title;
  calendarInput.data.url = url;
  calendarInput.data.user = principal.user;
  calendarInput.data.password = principal.password;
};

// preset of available calendar colors
const colors = [
  '#ff7b91',
  '#fe64b6',
  '#c276c5',
  '#b865ff',
  '#8fa5ff',
  '#64c2d0',
  '#64bead',
  '#73c690',
  '#e0ad6a',
  '#ff8b67',
];

// initially load data when component gets remounted
onMounted(async () => {
  const route = useRoute();
  const router = useRouter();

  // Error should be a string value, so don't worry about any obj deconstruction.
  if (route.query.error) {
    calendarConnectError.value = route.query.error as string;
    await router.replace(route.path);
  }

  await refresh();
});
</script>

<template>
<div class="flex flex-col gap-8">
  <div class="text-3xl font-thin text-gray-500 dark:text-gray-200">{{ t('heading.calendarSettings') }}</div>
  <div class="flex flex-col gap-6 pl-6">
    <alert-box
      @close="calendarConnectError = ''"
      title="Calendar Connect Error"
      v-if="calendarConnectError"
    >{{calendarConnectError}}</alert-box>

    <!-- list of possible calendars to connect -->
    <calendar-management
      :title="t('heading.calendarsUnconnected')"
      :type="CalendarManagementType.Connect"
      :calendars="calendarStore.unconnectedCalendars"
      :loading="loading"
      @sync="syncCalendars"
      @remove="deleteCalendar"
      @modify="connectCalendar"
    />

    <!-- list of connected calendars -->
    <calendar-management
      :title="t('heading.calendarsConnected')"
      :type="CalendarManagementType.Edit"
      :calendars="calendarStore.connectedCalendars"
      :loading="loading"
      @modify="editCalendar"
    />

    <div class="flex gap-4">
      <secondary-button
        :label="t('label.addCalendar', { provider: t('label.google') })"
        class="btn-add text-sm !text-teal-500"
        @click="addCalendar(CalendarProviders.Google)"
        :disabled="inputMode"
        :title="t('label.addCalendar', { provider: t('label.google') })"
      />
      <secondary-button
        :label="t('label.addCalendar', { provider: t('label.caldav') })"
        class="btn-add text-sm !text-teal-500"
        @click="addCalendar(CalendarProviders.Caldav)"
        :disabled="inputMode"
        :title="t('label.addCalendar', { provider: t('label.caldav') })"
      />
    </div>

    <!-- CalDAV calendar discovery -->
    <div class="hidden flex-col gap-6">
      <div class="text-lg">Discover CalDAV Calendars</div>
      <div class="flex max-w-2xl flex-col gap-4 pl-6">
        <label class="mt-4 flex items-center pl-4">
          <div class="w-full max-w-2xs">principal</div>
          <input
            v-model="principal.url"
            type="text"
            class="w-full max-w-sm rounded-md"
          />
        </label>
        <label class="flex items-center pl-4">
          <div class="w-full max-w-2xs">{{ t('label.username') }}</div>
          <input
            v-model="principal.user"
            type="text"
            class="w-full max-w-sm rounded-md"
          />
        </label>
        <label class="flex items-center pl-4">
          <div class="w-full max-w-2xs">{{ t('label.password') }}</div>
          <input
            v-model="principal.password"
            type="password"
            class="w-full max-w-sm rounded-md"
          />
        </label>
      </div>
      <div>
        <secondary-button
          :label="'Search for calendars'"
          class="btn-search text-sm !text-teal-500"
          :waiting="processPrincipal"
          @click="getRemoteCalendars"
          :title="t('label.search')"
        />
      </div>
      <div v-if="searchResultCalendars.length" class="flex max-w-2xl flex-col gap-2 pl-6">
        <div v-for="cal in searchResultCalendars" :key="cal.url" class="flex items-center gap-2">
          <div>{{ cal.title }}</div>
          <div>{{ cal.url }}</div>
          <button
            @click="assignCalendar(cal.title, cal.url)"
            class="btn-assign ml-auto flex items-center gap-0.5 rounded-full bg-teal-500 px-2 py-1 text-xs text-white"
            :title="t('label.assign')"
          >
            <icon-arrow-right class="size-3.5 fill-transparent stroke-white stroke-2" />
            {{ 'Select calendar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- set calendar connection data -->
    <div v-if="inputMode" class="flex max-w-2xl flex-col gap-4 pl-6">
      <div class="text-lg">
        <span v-if="isCalDav">{{ t('label.caldav') }}</span>
        <span v-if="isGoogle">{{ t('label.google') }}</span>
        &mdash;
        {{ addMode ? t('label.addCalendar') : t('label.editCalendar') }}
      </div>
      <div v-if="isGoogle && addMode" class="mb-4">
        <p class="mb-2 text-lg">{{ t('text.googlePermissionDisclaimer') }}</p>
        <ul class="text-md mx-8 list-disc">
          <li>
            <strong>
              {{ t('text.googlePermissionEventsName') }}
            </strong> - {{ t('text.googlePermissionEventReason') }}
          </li>
          <li>
            <strong>
              {{ t('text.googlePermissionCalendarName') }}
            </strong> - {{ t('text.googlePermissionCalendarReason') }}
          </li>
        </ul>
      </div>
      <label v-if="isCalDav || editMode" class="flex items-center pl-4">
        <div class="w-full max-w-2xs">{{ t('label.title') }}</div>
        <input
          v-model="calendarInput.data.title"
          type="text"
          class="w-full max-w-sm rounded-md"
        />
      </label>
      <label v-if="isCalDav || editMode" class="flex items-center pl-4">
        <div class="w-full max-w-2xs">{{ t('label.color') }}</div>
        <div class="flex w-full max-w-sm items-center gap-4">
          <select v-if="addMode" v-model="calendarInput.data.color" class="w-full rounded-md">
            <option v-for="color in colors" :key="color" :value="color" :style="{ backgroundColor: color }">
              {{ color }}
            </option>
          </select>
          <input v-else type="text" v-model="calendarInput.data.color" class="w-full rounded-md" />
          <div class="size-8 shrink-0 rounded-full" :style="{ backgroundColor: calendarInput.data.color }"></div>
        </div>
      </label>
      <label v-if="isCalDav" class="flex items-center pl-4">
        <div class="w-full max-w-2xs">{{ t('label.calendarUrl') }}</div>
        <input
          v-model="calendarInput.data.url"
          type="url"
          class="w-full max-w-sm rounded-md"
        />
      </label>
      <label v-if="isCalDav" class="flex items-center pl-4">
        <div class="w-full max-w-2xs">{{ t('label.username') }}</div>
        <input
          v-model="calendarInput.data.user"
          type="text"
          class="w-full max-w-sm rounded-md"
        />
      </label>
      <label v-if="isCalDav" class="flex items-center pl-4">
        <div class="w-full max-w-2xs">{{ t('label.password') }}</div>
        <input
          v-model="calendarInput.data.password"
          type="password"
          class="w-full max-w-sm rounded-md"
        />
      </label>
      <div class="flex justify-between gap-4">
        <div class="flex">
        <caution-button
          v-if="editMode"
          :label="t('label.disconnect')"
          class="btn-disconnect text-sm"
          @click="() => disconnectCalendar(calendarInput.id)"
          :title="t('label.disconnect')"
        />
        </div>
        <div class="flex gap-4 self-end">
        <secondary-button
          :label="t('label.cancel')"
          class="btn-cancel text-sm !text-teal-500"
          @click="resetInput"
          :title="t('label.cancel')"
        />
        <primary-button
          v-if="isCalDav || editMode"
          :label="addMode ? t('label.connectCalendar') : t('label.saveChanges')"
          class="btn-save text-sm"
          @click="saveCalendar"
          :title="t('label.save')"
        />
        <!-- Google Button -->
        <google-calendar-button
          v-if="isGoogle && addMode"
          class="btn-connect cursor-pointer"
          :title="t('label.signInWithGoogle')"
          :label="t('label.connectGoogleCalendar')"
          @click="saveCalendar"
        />
        </div>
      </div>
    </div>

  </div>
</div>
<!-- Calendar disconnect confirmation modal -->
<confirmation-modal
  :open="deleteCalendarModalOpen"
  :title="t('label.calendarDeletion')"
  :message="t('text.calendarDeletionWarning')"
  :confirm-label="t('label.calendarDeletion')"
  :cancel-label="t('label.cancel')"
  :useCautionButton="true"
  @confirm="deleteCalendarConfirm"
  @close="closeModals"
></confirmation-modal>
</template>
