<template>
  <!-- page title area -->
  <div v-if="user.exists()" class="flex flex-col gap-2 justify-center items-center">
    <div class="text-4xl font-light">{{ user.data.name }}</div>
    <div class="flex items-center gap-4">
      <div class="rounded-full text-xs uppercase border border-gray-500 text-gray-500 px-2">
        {{ keyByValue(subscriberLevels, user.data.level) }}
      </div>
      <div class="flex gap-1 text-gray-500">
        {{ user.data.timezone }}
        <router-link :to="{ name: 'settings' }" class="pt-0.5 cursor-pointer">
          <icon-pencil class="w-4 h-4 stroke-1.5" />
        </router-link>
      </div>
    </div>
    <div class="grid grid-cols-2 mt-8 mb-12 gap-8">
      <!-- calendars -->
      <div class="flex flex-col items-center">
        <div class="text-3xl font-semibold">{{ calendarStore.connectedCalendars.length }}/&infin;</div>
        <div class="text-gray-500 text-center">{{ t('heading.calendarsConnected') }}</div>
      </div>
      <!-- appointments -->
      <div class="flex flex-col items-center">
        <div class="text-3xl font-semibold">{{ appointmentStore.pendingAppointments.length }}</div>
        <div class="text-gray-500 text-center">{{ t('heading.pendingAppointments') }}</div>
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

// do log out
const logout = async () => {
  await user.logout(call);
  await router.push('/');
};

const editProfile = async () => {
  window.location = fxaEditProfileUrl;
};
</script>
