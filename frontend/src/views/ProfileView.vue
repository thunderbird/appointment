<script setup lang="ts">
import { inject, onMounted } from 'vue';
import { keyByValue } from '@/utils';
import { callKey, isFxaAuthKey, fxaEditProfileUrlKey } from '@/keys';
import { useI18n } from 'vue-i18n';
import { SubscriberLevels } from '@/definitions';
import { createUserStore } from '@/stores/user-store';
import { storeToRefs } from 'pinia';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import SecondaryButton from '@/elements/SecondaryButton.vue';

// icons
import { IconPencil } from '@tabler/icons-vue';
import { useRouter } from 'vue-router';

// Stores
import { createCalendarStore } from '@/stores/calendar-store';
import { createAppointmentStore } from '@/stores/appointment-store';

// component constants
const router = useRouter();
const { t } = useI18n();
const call = inject(callKey);
const fxaEditProfileUrl = inject(fxaEditProfileUrlKey);
const isFxaAuth = inject(isFxaAuthKey);

const appointmentStore = createAppointmentStore(call);
const calendarStore = createCalendarStore(call);
const user = createUserStore(call);

const { pendingAppointments } = storeToRefs(appointmentStore);
const { connectedCalendars } = storeToRefs(calendarStore);

// do log out
const logout = async () => {
  await user.logout();
  await router.push('/');
};

const editProfile = async () => {
  window.location.href = fxaEditProfileUrl;
};

// Load calendar and bookings information
onMounted(() => {
  calendarStore.fetch();
  appointmentStore.fetch();
});
</script>

<template>
  <!-- page title area -->
  <div v-if="user.authenticated" class="flex flex-col items-center justify-center gap-2">
    <div class="text-4xl font-light">{{ user.data.name }}</div>
    <div class="flex items-center gap-4">
      <div class="rounded-full border border-gray-500 px-2 text-xs uppercase text-gray-500">
        {{ keyByValue(SubscriberLevels, user.data.level, true) }}
      </div>
      <div class="flex gap-1 text-gray-500">
        {{ user.data.settings.timezone }}
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
    <secondary-button
      v-if="isFxaAuth"
      class="btn-edit mb-8"
      :label="t('label.editProfile')"
      @click="editProfile"
      :title="t('label.edit')"
    />
    <primary-button
      :label="t('label.logOut')"
      class="btn-logout"
      @click="logout"
      :title="t('label.logOut')"
    />
  </div>
</template>
