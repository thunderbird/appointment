<template>
  <!-- page title area -->
  <div v-if="user" class="flex flex-col gap-2 justify-center items-center">
    <div class="text-4xl font-light">{{ user.name }}</div>
    <div class="flex items-center gap-4">
      <div class="rounded-full text-xs uppercase border border-gray-500 text-gray-500 px-2">
        {{ keyByValue(subscriberLevels, user.level) }}
      </div>
      <div class="flex gap-1 text-gray-500">
        {{ user.timezone }}
        <router-link :to="{ name: 'settings' }" class="pt-0.5 cursor-pointer">
          <icon-pencil class="w-4 h-4 stroke-1.5" />
        </router-link>
      </div>
    </div>
    <div class="grid grid-cols-2 mt-8 mb-12 gap-8">
      <!-- calendars -->
      <div class="flex flex-col items-center">
        <div class="text-3xl font-semibold">{{ calendars.length }}/&infin;</div>
        <div class="text-gray-500 text-center">{{ t('heading.calendarsConnected') }}</div>
      </div>
      <!-- appointments -->
      <div class="flex flex-col items-center">
        <div class="text-3xl font-semibold">{{ pendingAppointments.length }}</div>
        <div class="text-gray-500 text-center">{{ t('heading.pendingAppointments') }}</div>
      </div>
    </div>
    <primary-button :label="t('label.logOut')" @click="logout()" />
  </div>
</template>

<script setup>
import { inject, computed, onMounted } from 'vue';
import { keyByValue } from '@/utils';
import { useI18n } from 'vue-i18n';
import { subscriberLevels, appointmentState } from '@/definitions';
import { removeUserFromStorage } from '@/stores/user-store';
import PrimaryButton from '@/elements/PrimaryButton';

// icons
import { IconPencil } from '@tabler/icons-vue';

// component constants
const auth = inject('auth');

// component constants
const { t } = useI18n();
const refresh = inject('refresh');

// view properties
const props = defineProps({
  calendars: Array, // list of calendars from db
  appointments: Array, // list of appointments from db
  user: Object, // currently logged in user, null if not logged in
});

// list of pending appointments
const pendingAppointments = computed(() => props.appointments.filter((a) => a.status === appointmentState.pending));

// do log out
const logout = () => {
  auth.logout({
    logoutParams: {
      returnTo: window.location.origin,
    },
  });
  removeUserFromStorage();
};

// initially load data when component gets remounted
onMounted(async () => {
  await refresh();
});
</script>
