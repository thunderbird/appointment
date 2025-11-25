<script setup lang="ts">
import { ref, inject, onMounted } from 'vue';
import { keyByValue } from '@/utils';
import { callKey, accountsTbProfileUrlKey } from '@/keys';
import { useI18n } from 'vue-i18n';
import { SubscriberLevels } from '@/definitions';
import { createUserStore } from '@/stores/user-store';
import { storeToRefs } from 'pinia';
import { PrimaryButton } from '@thunderbirdops/services-ui';

// icons
import { IconPencil } from '@tabler/icons-vue';
import { useRouter } from 'vue-router';

// Stores
import { createCalendarStore } from '@/stores/calendar-store';
import { createAppointmentStore } from '@/stores/appointment-store';
import { isFxaAuth, isOidcAuth } from "@/composables/authSchemes";

// component constants
const router = useRouter();
const { t } = useI18n();
const call = inject(callKey);
const accountsTbProfileUrl = inject(accountsTbProfileUrlKey);

const appointmentStore = createAppointmentStore(call);
const calendarStore = createCalendarStore(call);
const user = createUserStore(call);

const { connectedCalendars } = storeToRefs(calendarStore);

const pendingAppointmentsCount = ref<number>();

// do log out
const logout = async () => {
  await user.logout();
  await router.push('/');
};

const editProfile = async () => {
  window.location.href = accountsTbProfileUrl;
};

// Load calendar and bookings information
onMounted(async () => {
  calendarStore.fetch();

  const { data, error } = await appointmentStore.fetchPendingAppointmentsCount();

  if (!error.value) {
    pendingAppointmentsCount.value = data.value.count
  }
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
        <div class="text-3xl font-semibold">{{ pendingAppointmentsCount }}</div>
        <div class="text-center text-gray-500">{{ t('heading.pendingAppointments') }}</div>
      </div>
    </div>
    <primary-button
      v-if="isFxaAuth || isOidcAuth"
      class="btn-edit mb-8"
      variant="outline"
      :label="t('label.editProfile')"
      @click="editProfile"
      :title="t('label.edit')"
    >
      {{ t('label.edit') }}
    </primary-button>
    <primary-button
      :label="t('label.logOut')"
      class="btn-logout"
      @click="logout"
      :title="t('label.logOut')"
    >
      {{ t('label.logOut') }}
    </primary-button>
  </div>
</template>
