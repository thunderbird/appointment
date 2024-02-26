<template>
  <div class="flex max-w-2xl">
    <div class="text-xl">{{ title }}</div>
    <div class="mx-auto mr-0 inline-flex" v-if="type === calendarManagementType.connect">
      <secondary-button
        class="text-sm !text-teal-500 disabled:scale-100 disabled:opacity-50 disabled:shadow-none"
        :disabled="loading"
        @click="emit('sync')"
      >
        <span class="mr-2 inline-block">
          {{ t('label.syncCalendars') }}
        </span>
        <icon-refresh class="inline-block size-4 stroke-2" :class="{ 'animate-spin': loading }" />
      </secondary-button>
    </div>
  </div>
  <div v-if="filteredCalendars?.length" class="flex max-w-2xl flex-col gap-2 pl-6">
    <div v-for="cal in filteredCalendars" :key="cal.id" class="flex items-center gap-2">
      <div class="flex-center size-6 rounded-lg" :style="{ backgroundColor: cal.color ?? '#38bdf8' }">
        <icon-calendar class="size-4 stroke-white stroke-2"/>
      </div>
      <span class="calendar-title">
      {{ cal.title }}
      </span>
      <button
          v-if="type === calendarManagementType.connect"
          @click="emit('modify', cal.id)"
          :disabled="loading"
          class="
            ml-auto flex items-center gap-0.5 rounded-full bg-teal-500 px-2 py-1
            text-xs text-white disabled:scale-100 disabled:opacity-50 disabled:shadow-none
          "
      >
        <icon-arrow-right class="size-3 stroke-3"/>
        {{ t('label.connectCalendar') }}
      </button>
      <button
          v-if="type === calendarManagementType.edit"
          @click="emit('modify', cal.id)"
          :disabled="loading"
          class="
            ml-auto flex items-center gap-0.5 rounded-full bg-teal-500 px-2 py-1
            text-xs text-white disabled:scale-100 disabled:opacity-50 disabled:shadow-none
          "
      >
        <icon-pencil class="size-3 stroke-3"/>
        {{ t('label.editCalendar') }}
      </button>
      <button
        v-if="cal.connected"
        class="bg-transparent p-0.5 disabled:scale-100 disabled:opacity-50 disabled:shadow-none"
        :disabled="loading"
        @click="emit('remove', cal.id)"
      >
        <icon-x class="size-5 stroke-red-500 stroke-2"/>
      </button>
    </div>
  </div>
</template>

<script setup>
import { calendarManagementType } from '@/definitions';
import { computed } from 'vue';
import {
  IconArrowRight, IconCalendar, IconPencil, IconX, IconRefresh,
} from '@tabler/icons-vue';
import { useI18n } from 'vue-i18n';
import SecondaryButton from '@/elements/SecondaryButton';

const { t } = useI18n({ useScope: 'global' });
const emit = defineEmits(['modify', 'remove', 'sync']);

const props = defineProps({
  calendars: Array, // List of calendars to display
  title: String,
  type: {
    validator(value) {
      return Object.values(calendarManagementType).includes(value);
    },
  },
  loading: Boolean,
});

// Filter by connected or not connected depending on the list type
const filteredCalendars = computed(() => props.calendars.filter((calendar) => (
  props.type === calendarManagementType.edit ? calendar.connected : !calendar.connected
)));

</script>
