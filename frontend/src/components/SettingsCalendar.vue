<template>
<div class="flex flex-col gap-8">
  <div class="text-3xl text-gray-500 font-semibold">{{ t('heading.calendarSettings') }}</div>
  <div class="pl-6 flex flex-col gap-6">

    <!-- list of calendar connections -->
    <div class="text-xl">{{ t('heading.calendarConnections') }}</div>
    <div v-if="calendars?.length" class="pl-6 flex flex-col gap-2 max-w-2xl">
      <div v-for="cal in calendars" :key="cal.id" class="flex gap-2 items-center">
        <div class="flex-center w-6 h-6 rounded-lg" :style="{ backgroundColor: cal.color ?? '#38bdf8' }">
          <icon-calendar class="w-4 h-4 fill-transparent stroke-2 stroke-white" />
        </div>
        {{ cal.title }}
        <button
          @click="editCalendar(cal.id)"
          class="ml-auto flex items-center gap-0.5 px-2 py-1 rounded-full bg-teal-500 text-white text-xs"
        >
          <icon-pencil class="h-3 w-3 stroke-2 stroke-white fill-transparent" />
          {{ t('label.editCalendar') }}
        </button>
        <div class="p-0.5 cursor-pointer" @click="deleteCalendar(cal.id)">
          <icon-x class="h-5 w-5 stroke-2 stroke-red-500 fill-transparent" />
        </div>
      </div>
    </div>
    <div class="flex gap-4">
      <secondary-button
        :label="t('label.addCalendar', { provider: t('label.google') })"
        class="text-sm !text-teal-500"
        @click="addCalendar(calendarProviders.google)"
        :disabled="inputMode"
      />
      <secondary-button
        :label="t('label.addCalendar', { provider: t('label.caldav') })"
        class="text-sm !text-teal-500"
        @click="addCalendar(calendarProviders.caldav)"
        :disabled="inputMode"
      />
    </div>

    <!-- add CalDAV calendar connection -->
    <div class="hidden flex flex-col gap-6">
      <div class="text-lg">Discover CalDAV Calendars</div>
      <div class="pl-6 flex flex-col gap-4 max-w-2xl">
        <label class="pl-4 mt-4 flex items-center">
          <div class="w-full max-w-2xs">principal</div>
          <input
            v-model="principal.url"
            type="text"
            class="w-full max-w-sm rounded-md w-full"
          />
        </label>
        <label class="pl-4 flex items-center">
          <div class="w-full max-w-2xs">{{ t('label.username') }}</div>
          <input
            v-model="principal.user"
            type="text"
            class="w-full max-w-sm rounded-md w-full"
          />
        </label>
        <label class="pl-4 flex items-center">
          <div class="w-full max-w-2xs">{{ t('label.password') }}</div>
          <input
            v-model="principal.password"
            type="password"
            class="w-full max-w-sm rounded-md w-full"
          />
        </label>
      </div>
      <div>
        <secondary-button
          :label="'Search for calendars'"
          class="text-sm !text-teal-500"
          :waiting="processPrincipal"
          @click="getRemoteCalendars"
        />
      </div>
      <div v-if="searchResultCalendars.length" class="pl-6 flex flex-col gap-2 max-w-2xl">
        <div v-for="cal in searchResultCalendars" :key="cal.url" class="flex gap-2 items-center">
          <div>{{ cal.title }}</div>
          <div>{{ cal.url }}</div>
          <button
            @click="assignCalendar(cal.title, cal.url)"
            class="ml-auto flex items-center gap-0.5 px-2 py-1 rounded-full bg-teal-500 text-white text-xs"
          >
            <icon-arrow-right class="h-3.5 w-3.5 stroke-2 stroke-white fill-transparent" />
            {{ 'Select calendar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- set calendar connection data -->
    <div v-if="inputMode" class="pl-6 flex flex-col gap-4 max-w-2xl">
      <div class="text-lg">
        <span v-if="isCalDav">{{ t('label.caldav') }}</span>
        <span v-if="isGoogle">{{ t('label.google') }}</span>
        &mdash;
        {{ inputMode === inputModes.add ? t('label.addCalendar') : t('label.editCalendar') }}
      </div>
      <label v-if="isCalDav || inputMode === inputModes.edit" class="pl-4 flex items-center">
        <div class="w-full max-w-2xs">{{ t('label.title') }}</div>
        <input
          v-model="calendarInput.data.title"
          type="text"
          class="w-full max-w-sm rounded-md w-full"
        />
      </label>
      <label v-if="isCalDav || inputMode === inputModes.edit" class="pl-4 flex items-center">
        <div class="w-full max-w-2xs">{{ t('label.color') }}</div>
        <div class="flex gap-4 items-center w-full max-w-sm">
          <select v-if="inputMode === inputModes.add" v-model="calendarInput.data.color" class="rounded-md w-full">
            <option v-for="color in colors" :key="color" :value="color" :style="{ backgroundColor: color }">
              {{ color }}
            </option>
          </select>
          <input v-else type="text" v-model="calendarInput.data.color" class="rounded-md w-full" />
          <div class="w-8 h-8 rounded-full shrink-0" :style="{ backgroundColor: calendarInput.data.color }"></div>
        </div>
      </label>
      <label v-if="isCalDav" class="pl-4 flex items-center">
        <div class="w-full max-w-2xs">{{ t('label.calendarUrl') }}</div>
        <input
          v-model="calendarInput.data.url"
          type="url"
          class="w-full max-w-sm rounded-md w-full"
        />
      </label>
      <label class="pl-4 flex items-center">
        <div class="w-full max-w-2xs">
          <span v-if="isCalDav">{{ t('label.username') }}</span>
          <span v-if="isGoogle">{{ t('label.email') }}</span>
        </div>
        <input
          v-model="calendarInput.data.user"
          type="text"
          class="w-full max-w-sm rounded-md w-full"
        />
      </label>
      <label v-if="isCalDav" class="pl-4 flex items-center">
        <div class="w-full max-w-2xs">{{ t('label.password') }}</div>
        <input
          v-model="calendarInput.data.password"
          type="password"
          class="w-full max-w-sm rounded-md w-full"
        />
      </label>
      <div class="self-end flex gap-4">
        <secondary-button
          :label="t('label.cancel')"
          class="text-sm !text-teal-500"
          @click="resetInput"
        />
        <primary-button
          :label="inputMode === inputModes.add ? t('label.connectCalendar') : t('label.saveChanges')"
          class="text-sm"
          @click="saveCalendar"
        />
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import {
  ref, reactive, inject, onMounted, computed,
} from 'vue';
import { useI18n } from 'vue-i18n';
import SecondaryButton from '@/elements/SecondaryButton';
import PrimaryButton from '@/elements/PrimaryButton';

// icons
import {
  IconArrowRight,
  IconCalendar,
  IconPencil,
  IconX,
} from '@tabler/icons-vue';

// component constants
const { t } = useI18n({ useScope: 'global' });
const call = inject('call');
const refresh = inject('refresh');

// view properties
defineProps({
  calendars: Array, // list of calendars from db
});

// handle calendar user input to add or edit calendar connections
const inputModes = {
  hidden: 0,
  add: 1,
  edit: 2,
};
const inputMode = ref(inputModes.hidden);

// supported calendar providers
const calendarProviders = {
  caldav: 1,
  google: 2,
};
const defaultCalendarInput = {
  provider: calendarProviders.caldav,
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
const isCalDav = computed(() => calendarInput.data.provider === calendarProviders.caldav);
const isGoogle = computed(() => calendarInput.data.provider === calendarProviders.google);

// clear input fields
const resetInput = () => {
  calendarInput.id = null;
  calendarInput.data = { ...defaultCalendarInput };
  inputMode.value = inputModes.hidden;
};

// set input mode for adding or editing
const addCalendar = (provider) => {
  inputMode.value = inputModes.add;
  calendarInput.data.provider = provider;
};
const editCalendar = async (id) => {
  inputMode.value = inputModes.edit;
  calendarInput.id = id;
  const { data } = await call(`cal/${id}`).get().json();
  Object.keys(data.value).forEach((attr) => {
    calendarInput.data[attr] = data.value[attr];
  });
};

// do remove a given calendar connection
const deleteCalendar = async (id) => {
  await call(`cal/${id}`).delete();
  refresh();
};

// do save calendar data
const saveCalendar = async () => {
  // add new caldav calendar
  if (isCalDav.value && inputMode.value === inputModes.add) {
    await call('cal').post(calendarInput.data);
  }
  // add all google calendars connected to given gmail address
  if (isGoogle.value && inputMode.value === inputModes.add) {
    const googleUrl = await call('google/auth').get();
    window.open(googleUrl.data.value.slice(1, -1));
  }
  // edit existing calendar connection
  if (inputMode.value === inputModes.edit) {
    await call(`cal/${calendarInput.id}`).put(calendarInput.data);
  }
  // refresh list of calendars
  refresh();
  resetInput();
};

// discover calendars by principal
const principal = reactive({
  url: '',
  user: '',
  password: '',
});
const processPrincipal = ref(false);
const searchResultCalendars = ref([]);
const getRemoteCalendars = async () => {
  processPrincipal.value = true;
  const { error, data } = await call('rmt/calendars').post(principal);
  searchResultCalendars.value = !error.value ? JSON.parse(data.value) : [];
  processPrincipal.value = false;
};

// fill input form with data from principal discovery
const assignCalendar = (title, url) => {
  inputMode.value = inputModes.add;
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
  '#ff8b67 ',
];

// initially load data when component gets remounted
onMounted(async () => {
  await refresh();
});
</script>
