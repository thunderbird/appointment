<template>
  <div class="flex flex-col gap-8">
    <div class="text-3xl text-gray-500 font-semibold">{{ t('heading.accountSettings') }}</div>
    <div class="pl-6">
      <div class="text-xl">{{ t('heading.accountData') }}</div>
      <div class="pl-6 mt-6">
        <div class="text-lg">{{ t('text.accountDataNotice') }}</div>
        <primary-button
            :label="t('label.downloadYourData')"
            class="text-sm"
            @click="downloadData"
        />
      </div>
    </div>
    <div class="pl-6">
      <div class="text-xl">{{ t('heading.accountDeletion') }}</div>
      <div class="pl-6 mt-6">
        <div class="text-lg">{{ t('text.accountDeletionWarning') }}</div>
        <primary-button
            :label="t('label.deleteYourAccount')"
            class="text-sm"
            @click="deleteAccount"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { colorSchemes } from '@/definitions';
import {
  ref, reactive, inject, watch,
} from 'vue';
import { useI18n } from 'vue-i18n';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import { useAuth0 } from '@auth0/auth0-vue';
import { useRouter } from 'vue-router';
// import SwitchToggle from '@/elements/SwitchToggle';

// component constants
const { t, locale, availableLocales } = useI18n({ useScope: 'global' });
const call = inject('call');
const dj = inject('dayjs');
const router = useRouter();
const auth0 = useAuth0();

// view properties
const props = defineProps({
  user: Object, // currently logged in user, null if not logged in
});

// do remove a given calendar connection
const downloadData = async () => {
  const { data } = await call('account/download').get().blob();
  if (!data || !data.value) {
    console.error('Failed to download blob!!');
    return;
  }
  // Data is a ref to our new blob
  const fileObj = window.URL.createObjectURL(data.value);
  window.location.assign(fileObj);
};

const deleteAccount = async () => {
  const { error } = await call('account/delete').delete();

  if (error.value) {
    console.warn('ERROR: ', error.value);
    return;
  }

  if (auth0) {
    await auth0.logout({
      logoutParams: {
        returnTo: window.location.origin,
      },
    });
  } else {
    await router.push('/');
  }
};

// handle ui languages
watch(locale, (newValue) => {
  localStorage.setItem('locale', newValue);
});

// handle theme mode
const initialTheme = localStorage.getItem('theme')
  ? colorSchemes[localStorage.getItem('theme')]
  : colorSchemes.system;
const theme = ref(initialTheme);
watch(theme, (newValue) => {
  switch (newValue) {
    case colorSchemes.dark:
      localStorage.setItem('theme', 'dark');
      document.documentElement.classList.add('dark');
      break;
    case colorSchemes.light:
      localStorage.setItem('theme', 'light');
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

// handle theme mode
const detectedTimeFormat = Number(dj('2022-05-24 20:00:00').format('LT').split(':')[0]) > 12 ? 24 : 12;
const initialTimeFormat = localStorage.getItem('timeFormat') ?? detectedTimeFormat;
const timeFormat = ref(initialTimeFormat);
watch(timeFormat, (newValue) => {
  localStorage.setItem('timeFormat', newValue);
});

// timezones
const activeTimezone = reactive({
  primary: props.user?.timezone ?? dj.tz.guess(),
  secondary: dj.tz.guess(),
});
const timezones = Intl.supportedValuesOf('timeZone');
// load user defined timezone on page reload
watch(
  () => props.user,
  (loadedUser) => {
    activeTimezone.primary = loadedUser.timezone;
  },
);

// save timezone config
const updateTimezone = async () => {
  const { error } = await call('me').put({ timezone: activeTimezone.primary }).json();
  if (!error) {
    // TODO show some confirmation
  }
};
</script>
