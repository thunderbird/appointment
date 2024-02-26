<template>
  <!-- page title area -->
  <div v-if="user.exists()" class="flex flex-col items-center justify-center gap-2">
    <div class="text-4xl font-light">{{ user.data.name }}</div>
    <div class="flex items-center gap-4">
      <div class="rounded-full border border-gray-500 px-2 text-xs uppercase text-gray-500">
        {{ keyByValue(subscriberLevels, user.data.level) }}
      </div>
      <div class="flex gap-1 text-gray-500">
        {{ user.data.timezone }}
        <router-link :to="{ name: 'settings' }" class="cursor-pointer pt-0.5">
          <icon-pencil class="stroke-1.5 size-4" />
        </router-link>
      </div>
    </div>
    <div class="mb-12 mt-8 grid grid-cols-2 gap-8">
      <!-- calendars -->
      <div class="flex flex-col items-center">
        <div class="text-3xl font-semibold">{{ connectedCalendars.length }}</div>
        <div class="text-center text-gray-500">{{ t('heading.calendarsConnected') }}</div>
      </div>
      <!-- appointments -->
      <div class="flex flex-col items-center">
        <div class="text-3xl font-semibold">{{ pendingAppointments.length }}</div>
        <div class="text-center text-gray-500">{{ t('heading.pendingAppointments') }}</div>
      </div>
    </div>
    <secondary-button class="mb-8" v-if="isFxaAuth" :label="t('label.editProfile')" @click="editProfile" />
    <primary-button :label="t('label.logOut')" @click="logout" />
  </div>
</template>

<script setup>
import { inject } from 'vue';
import { keyByValue } from '@/utils';
import { useI18n } from 'vue-i18n';
import { subscriberLevels } from '@/definitions';
import { useUserStore } from '@/stores/user-store';
import { storeToRefs } from 'pinia';
import PrimaryButton from '@/elements/PrimaryButton';
import SecondaryButton from '@/elements/SecondaryButton';

// icons
import { IconPencil } from '@tabler/icons-vue';
import { useRouter } from 'vue-router';

// Stores
import { useCalendarStore } from '@/stores/calendar-store';
import { useAppointmentStore } from '@/stores/appointment-store';

// component constants
const user = useUserStore();
const router = useRouter();

// component constants
const { t } = useI18n();
const call = inject('call');
const fxaEditProfileUrl = inject('fxaEditProfileUrl');
const isFxaAuth = inject('isFxaAuth');

const appointmentStore = useAppointmentStore();
const calendarStore = useCalendarStore();
const { pendingAppointments } = storeToRefs(appointmentStore);
const { connectedCalendars } = storeToRefs(calendarStore);

// do log out
const logout = async () => {
  await user.logout(call);
  await router.push('/');
};

const editProfile = async () => {
  window.location = fxaEditProfileUrl;
};
</script>
