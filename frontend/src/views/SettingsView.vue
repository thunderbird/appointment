<template>
  <!-- page title area -->
  <div class="flex justify-between items-start select-none">
    <div class="text-4xl font-light">{{ t('label.settings') }}</div>
  </div>
  <div class="flex justify-between gap-24 mt-8 pb-16 items-stretch">
    <!-- sidebar navigation -->
    <div class="w-1/5 flex flex-col gap-6">
      <!-- search -->
      <label class="flex items-center relative">
        <icon-search
          class="
            absolute top-1/2 -translate-y-1/2 left-4 cursor-text h-4 w-4 stroke-2
            stroke-gray-300 dark:stroke-gray-500 fill-transparent
          "
        /> 
        <input
          class="w-full text-sm pl-12 pr-2 rounded-md"
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
          rounded-lg font-semibold p-4 cursor-pointer flex justify-between
          text-gray-500 dark:text-gray-300 bg-gray-100 dark:bg-gray-600
        "
        :class="{ '!bg-teal-500 !text-white': view === activeView }"
        @click="show(key)"
      >
        <span>{{ t('label.' + key) }}</span>
        <icon-chevron-right
          class="
            h-6 w-6 stroke-1 fill-transparent rotate-180 transition-transform
            stroke-gray-800 dark:stroke-gray-300
          "
          :class="{ '!rotate-0 !stroke-white': view === activeView }"
        />
      </div>
    </div>
    <!-- content -->
    <div class="w-4/5 pt-14">

      <!-- general settings -->
      <div v-if="activeView === settingsSections.general" class="flex flex-col gap-8">
        <div class="text-3xl text-gray-500 font-semibold">{{ t('heading.generalSettings') }}</div>
        <div class="pl-6">
          <div class="text-xl">{{ t('heading.languageAndAppearance') }}</div>
          <div class="pl-6 mt-6">
            <div class="text-lg">{{ t('label.language') }}</div>
            <label class="pl-4 mt-4 flex items-center">
              <div class="w-full max-w-2xs">{{ t('label.language') }}</div>
              <select class="w-full max-w-sm rounded-md w-full">
                <option value="en-us">English (US)</option>
                <option value="de-de">German</option>
              </select>
            </label>
          </div>
          <div class="pl-6 mt-6">
            <div class="text-lg">{{ t('label.appearance') }}</div>
            <label class="pl-4 mt-4 flex items-center">
              <div class="w-full max-w-2xs">{{ t('label.theme') }}</div>
              <select v-model="theme" class="w-full max-w-sm rounded-md w-full">
                <option v-for="(key, label) in colorSchemes" :key="key" :value="key">
                  {{ t('label.' + label) }}
                </option>
              </select>
            </label>
            <label class="pl-4 mt-4 flex items-center">
              <div class="w-full max-w-2xs">{{ t('label.defaultFont') }}</div>
              <select class="w-full max-w-sm rounded-md w-full">
                <option value="os">Open Sans</option>
                <option value="fs">Fira Sans</option>
              </select>
            </label>
          </div>
        </div>
        <div class="pl-6">
          <div class="text-xl">{{ t('heading.dateAndTimeFormatting') }}</div>
          <div class="pl-6 mt-6 inline-grid grid-cols-2 gap-y-8 gap-x-16">
            <div class="text-lg">{{ t('label.timeFormat') }}</div>
            <div class="text-lg">{{ t('label.dateFormat') }}</div>
            <label class="pl-4 flex gap-4 items-center cursor-pointer">
              <input type="radio" name="timeFormat" class="text-teal-500" />
              <div class="w-full max-w-2xs">{{ t('label.12hAmPm') }}</div>
            </label>
            <label class="pl-4 flex gap-4 items-center cursor-pointer">
              <input type="radio" name="dateFormat" class="text-teal-500" />
              <div class="w-full max-w-2xs">{{ t('label.DDMMYYYY') }}</div>
            </label>
            <label class="pl-4 flex gap-4 items-center cursor-pointer">
              <input type="radio" name="timeFormat" class="text-teal-500" />
              <div class="w-full max-w-2xs">{{ t('label.24h') }}</div>
            </label>
            <label class="pl-4 flex gap-4 items-center cursor-pointer">
              <input type="radio" name="dateFormat" class="text-teal-500" />
              <div class="w-full max-w-2xs">{{ t('label.MMDDYYYY') }}</div>
            </label>
          </div>
          <div class="pl-6 mt-6">
            <div class="text-lg">{{ t('label.timeZone') }}</div>
            <label class="pl-4 mt-4 flex items-center">
              <div class="w-full max-w-2xs">{{ t('label.primaryTimeZone') }}</div>
              <select v-model="activeTimezone.primary" class="w-full max-w-sm rounded-md w-full">
                <option v-for="t in timezones" :key="t" :value="t">
                  UTC <span v-if="t > 0">+</span>{{ t }}
                </option>
              </select>
            </label>
            <label class="pl-4 mt-6 flex items-center">
              <div class="w-full max-w-2xs">{{ t('label.showSecondaryTimeZone') }}</div>
              <switch-toggle :active="true" />
            </label>
            <label class="pl-4 mt-6 flex items-center">
              <div class="w-full max-w-2xs">{{ t('label.secondaryTimeZone') }}</div>
              <select v-model="activeTimezone.secondary" class="w-full max-w-sm rounded-md w-full">
                <option v-for="t in timezones" :key="t" :value="t">
                  UTC <span v-if="t > 0">+</span>{{ t }}
                </option>
              </select>
            </label>
          </div>
        </div>
      </div>

      <!-- calendar settings -->
      <div v-if="activeView === settingsSections.calendar" class="flex flex-col gap-8">
        <div class="text-3xl text-gray-500 font-semibold">{{ t('heading.calendarSettings') }}</div>
        <div class="pl-6 flex flex-col gap-6">
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
              <button @click="assignCalendar(cal.title, cal.url)" class="ml-auto flex items-center gap-0.5 px-2 py-1 rounded-full bg-teal-500 text-white text-xs">
                <icon-arrow-right class="h-3.5 w-3.5 stroke-2 stroke-white fill-transparent" />
                {{ 'Select calendar' }}
              </button>
            </div>
          </div>
          <div class="text-xl">{{ t('heading.calendarConnections') }}</div>
          <div v-if="calendars?.length" class="pl-6 flex flex-col gap-2 max-w-2xl">
            <div v-for="cal in calendars" :key="cal.id" class="flex gap-2 items-center">
              <div class="flex-center w-6 h-6 rounded-lg" :style="{ backgroundColor: cal.color ?? '#38bdf8' }">
                <icon-calendar class="w-4 h-4 fill-transparent stroke-2 stroke-white" />
              </div>
              {{ cal.title }}
              <button @click="editCalendar(cal.id)" class="ml-auto flex items-center gap-0.5 px-2 py-1 rounded-full bg-teal-500 text-white text-xs">
                <icon-pencil class="h-3 w-3 stroke-2 stroke-white fill-transparent" />
                {{ t('label.editCalendar') }}
              </button>
              <div class="p-0.5 cursor-pointer" @click="deleteCalendar(cal.id)">
                <icon-x class="h-5 w-5 stroke-2 stroke-red-500 fill-transparent" />
              </div>
            </div>
          </div>
          <div v-if="!inputMode">
            <secondary-button
              :label="t('label.addCalendar')"
              class="text-sm !text-teal-500"
              @click="addCalendar"
            />
          </div>
          <div v-if="inputMode" class="pl-6 flex flex-col gap-4 max-w-2xl">
            <div class="text-lg">
              {{ t('label.caldav') }} &mdash; {{ inputMode === inputModes.add ? t('label.addCalendar') : t('label.editCalendar') }}
            </div>
            <label class="pl-4 flex items-center">
              <div class="w-full max-w-2xs">{{ t('label.title') }}</div>
              <input
                v-model="calendarInput.data.title"
                type="text"
                class="w-full max-w-sm rounded-md w-full"
              />
            </label>
            <label class="pl-4 flex items-center">
              <div class="w-full max-w-2xs">{{ t('label.color') }}</div>
              <select v-model="calendarInput.data.color" class="w-full max-w-sm rounded-md w-full">
                <option v-for="color in colors" :key="color" :value="color" :style="{ backgroundColor: color }">
                  {{ color }}
                </option>
              </select>
            </label>
            <label class="pl-4 flex items-center">
              <div class="w-full max-w-2xs">{{ t('label.calendarUrl') }}</div>
              <input
                v-model="calendarInput.data.url"
                type="url"
                class="w-full max-w-sm rounded-md w-full"
              />
            </label>
            <label class="pl-4 flex items-center">
              <div class="w-full max-w-2xs">{{ t('label.username') }}</div>
              <input
                v-model="calendarInput.data.user"
                type="text"
                class="w-full max-w-sm rounded-md w-full"
              />
            </label>
            <label class="pl-4 flex items-center">
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
                :label="inputMode === inputModes.add ? t('label.addCalendar') : t('label.saveChanges')"
                class="text-sm"
                @click="saveCalendar"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- appointments and booking settings -->
      <div v-if="activeView === settingsSections.appointmentsAndBooking">
        <div class="text-3xl text-gray-500 font-semibold">{{ t('heading.appointmentsAndBookingSettings') }}</div>
      </div>

      <!-- account settings -->
      <div v-if="activeView === settingsSections.account">
        <div class="text-3xl text-gray-500 font-semibold">{{ t('heading.accountSettings') }}</div>
      </div>

      <!-- privacy settings -->
      <div v-if="activeView === settingsSections.privacy">
        <div class="text-3xl text-gray-500 font-semibold">{{ t('heading.privacySettings') }}</div>
      </div>

      <!-- faq settings -->
      <div v-if="activeView === settingsSections.faq">
        <div class="text-3xl text-gray-500 font-semibold">{{ t('heading.frequentlyAskedQuestions') }}</div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive, inject, watch } from 'vue';
import { settingsSections, colorSchemes } from '@/definitions';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import SwitchToggle from '@/elements/SwitchToggle';
import SecondaryButton from '@/elements/SecondaryButton';
import PrimaryButton from '@/elements/PrimaryButton';

// icons
import {
  IconArrowRight,
  IconChevronRight,
  IconSearch,
  IconCalendar,
  IconPencil,
  IconX,
} from '@tabler/icons-vue';

// component constants
const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const call = inject('call');
const refresh = inject('refresh');

// view properties
defineProps({
  calendars:    Array,  // list of calendars from db
  appointments: Array,  // list of appointments from db
  user:         Object, // currently logged in user, null if not logged in
});

// menu navigation of different views
const activeView = ref(route.params.view ? settingsSections[route.params.view] : settingsSections.general);
const show = (key) => {
  router.replace({ name: route.name, params: { view: key } });
  activeView.value = settingsSections[key];
};

// handle theme mode
const initialTheme = !('theme' in localStorage) ? colorSchemes.system : colorSchemes[localStorage.theme]
const theme = ref(initialTheme);
watch(theme, (newValue) => {
	switch (newValue) {
		case colorSchemes.dark:
			localStorage.theme = 'dark';
			document.documentElement.classList.add('dark');
			break;
		case colorSchemes.light:
			localStorage.theme = 'light';
			document.documentElement.classList.remove('dark');
			break;
		case colorSchemes.system:
			localStorage.removeItem('theme');
			if (!window.matchMedia('(prefers-color-scheme: dark)').matches) {
				document.documentElement.classList.remove('dark');
			} else {
				document.documentElement.classList.add('dark');
			}
			break;
		default:
			break;
	}
});

// TODO: timezones
const activeTimezone = reactive({
  primary:   0,
  secondary: 4,
});
const timezones = Array.from(new Array(27), (_, i) => i + -12);

// calendar user input to add or edit calendar connection
const inputModes = {
  hidden: 0,
  add:    1,
  edit:   2,
};
const inputMode = ref(inputModes.hidden);
const defaultCalendarInput = {
  title:    '',
  color:    '',
  url:      '',
  user:     '',
  password: '',
};
const calendarInput = reactive({
  id: null,
  data: { ...defaultCalendarInput }
});

// clear input fields
const resetInput = () => {
  calendarInput.id = null;
  calendarInput.data = { ...defaultCalendarInput };
  inputMode.value = inputModes.hidden;
};

// set input mode for adding or editing
const addCalendar = () => {
  inputMode.value = inputModes.add;
};
const editCalendar = async (id) => {
  inputMode.value = inputModes.edit;
  calendarInput.id = id;
  const { data } = await call('cal/' + id).get().json();
  for (const attr in data.value) {
    calendarInput.data[attr] = data.value[attr];
  }
};
const assignCalendar = (title, url) => {
  inputMode.value = inputModes.edit;
  calendarInput.data.title = title;
  calendarInput.data.url = url;
  calendarInput.data.user = principal.user;
  calendarInput.data.user = principal.password;
};

// do remove a given calendar connection
const deleteCalendar = async (id) => {
  await call("cal/" + id).delete();
  refresh();
};

// do save calendar data
const saveCalendar = async () => {
  if (inputMode.value === inputModes.add) {
    await call("cal").post(calendarInput.data);
  }
  if (inputMode.value === inputModes.edit) {
    await call("cal/" + calendarInput.id).put(calendarInput.data);
  }
  refresh();
  resetInput();
};

// discover calendars by principal
const principal = reactive({
  url:      '',
  user:     '',
  password: '',
});
const processPrincipal = ref(false);
const searchResultCalendars = ref([]);
const getRemoteCalendars = async () => {
  processPrincipal.value = true;
  const { error, data } = await call("rmt/calendars").post(principal);
  searchResultCalendars.value = !error.value ? JSON.parse(data.value) : [];
  processPrincipal.value = false;
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
</script>
