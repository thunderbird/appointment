<template>
  <div
    class="rounded border-l-8 border-sky-400"
    :class="{
      'opacity-50 bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400': isPast,
      'cursor-pointer hover:shadow-md hover:bg-sky-400/10': !isPast,
    }"
    :style="{ borderColor: appointment.calendar_color }"
    @mouseover="el => !isPast ? paintBackground(el, appointment.calendar_color, '22') : null"
    @mouseout="el => !isPast ? paintBackground(el, appointment.calendar_color, _, true) : null"
  >
    <div
      class="
        h-full px-4 py-3 rounded-r border-solid border-t-2 border-r-2 border-b-2 flex flex-col gap-1
        border-sky-400
      "
      :class="{ 'border-dashed': isPending }"
      :style="{ borderColor: appointment.calendar_color }"
    >
      <div>{{ appointment.title }}</div>
      <div class="text-sm flex items-center gap-1">
        <icon-clock class="h-4 w-4 stroke-gray-500 stroke-2 fill-transparent shrink-0" />
        {{ t('label.' + keyByValue(appointmentState, appointment.status)) }}
      </div>
      <div class="text-sm flex items-center gap-1">
        <icon-calendar class="h-4 w-4 stroke-gray-500 stroke-2 fill-transparent shrink-0" />
        {{ appointment.calendar_title }}
      </div>
      <div class="pr-4 text-sm flex items-center gap-1">
        <icon-bulb class="h-4 w-4 stroke-gray-500 stroke-2 fill-transparent shrink-0" />
        <switch-toggle
          :label="t('label.activeAppointment')"
          :active="appointment.active"
          :disabled="true"
          @click.stop="null"
        />
      </div>
      <div class="text-sm flex items-center gap-1">
        <icon-link class="h-4 w-4 stroke-gray-500 stroke-2 fill-transparent shrink-0" />
        <div class="truncate">
          <a
            :href="bookingUrl + appointment.slug"
            class="text-teal-500 underline underline-offset-2"
            target="_blank"
            @click.stop="null"
          >
            {{ bookingUrl + appointment.slug }}
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { appointmentState } from '@/definitions';
import { inject, computed } from 'vue';
import { keyByValue } from '@/utils';
import { useI18n } from 'vue-i18n';
import SwitchToggle from '@/elements/SwitchToggle';

// icons
import {
  IconBulb,
  IconCalendar,
  IconClock,
  IconLink,
} from '@tabler/icons-vue';

// component constants
const { t } = useI18n();
const bookingUrl = inject('bookingUrl');
const paintBackground = inject('paintBackground');

// component properties
const props = defineProps({
  appointment: Object, // appointment to show details for
});

// true if an appointment from the past was given
const isPast = computed(() => props.appointment.status === appointmentState.past);

// true if a pending appointment was given
const isPending = computed(() => props.appointment.status === appointmentState.pending);
</script>
