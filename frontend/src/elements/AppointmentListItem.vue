<script setup lang="ts">
import { inject } from 'vue';
import { useI18n } from 'vue-i18n';
import { durationHumanizedKey } from '@/keys';
import { Appointment } from '@/models';

// icons
import { IconDotsVertical } from '@tabler/icons-vue';

// component constants
const durationHumanized = inject(durationHumanizedKey);
const { t } = useI18n();

// component properties
interface Props {
  appointment: Appointment; // appointment to show details for
};
defineProps<Props>();

</script>

<template>
  <div class="flex items-stretch gap-2">
    <div class="w-1.5 shrink-0 rounded-lg" :style="{ backgroundColor: appointment.calendar_color }"></div>
    <div class="w-[95%]">
      <div class="flex justify-between">
        <div class="overflow-x-hidden">
          <div class="truncate">{{ appointment.title }}</div>
          <div class="text-sm">
            <span v-if="appointment.duration">{{ durationHumanized(appointment.duration) }}</span>
          </div>
        </div>
        <icon-dots-vertical class="size-6 shrink-0 fill-gray-400 stroke-gray-400 stroke-2" />
      </div>
      <div class="flex items-center justify-between">
        <router-link
          :to="{ name: 'appointments', params: { 'slug': appointment.slug } }"
          class="shrink text-sm text-teal-500 underline underline-offset-2"
        >
          {{ t('label.viewBooking') }}
        </router-link>
      </div>
    </div>
  </div>
</template>
