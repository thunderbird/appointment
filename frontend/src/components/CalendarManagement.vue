<script setup lang="ts">
import { computed } from 'vue';
import {
  IconArrowRight, IconCalendar, IconPencil, IconX, IconRefresh,
} from '@tabler/icons-vue';
import { useI18n } from 'vue-i18n';
import { CalendarManagementType } from '@/definitions';
import { Calendar } from '@/models';
import SecondaryButton from '@/tbpro/elements/SecondaryButton.vue';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';

const { t } = useI18n({ useScope: 'global' });
const emit = defineEmits(['modify', 'remove', 'sync']);

// component properties
interface Props {
  calendars: Calendar[], // List of calendars to display
  title: string,
  type: CalendarManagementType,
  loading: boolean,
}
const props = defineProps<Props>();

// Filter by connected or not connected depending on the list type
const filteredCalendars = computed(() => props.calendars.filter((calendar: Calendar) => (
  props.type === CalendarManagementType.Edit ? calendar.connected : !calendar.connected
)));

</script>

<template>
  <div class="flex max-w-2xl">
    <div class="text-xl">{{ title }}</div>
    <div class="mx-auto mr-0 inline-flex" v-if="type === CalendarManagementType.Connect">
      <secondary-button
        class="btn-sync"
        :disabled="loading"
        @click="emit('sync')"
        :title="t('label.sync')"
        data-testid="calendar-settings-sync-calendars-button"
      >
        <template v-slot:icon>
          <icon-refresh class="size-4 stroke-2" :class="{ 'animate-spin': loading }" />
        </template>
        <span class="mr-2 inline-block">
          {{ t('label.syncCalendars') }}
        </span>
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
      <primary-button
        v-if="type === CalendarManagementType.Connect"
        @click="emit('modify', cal.id)"
        :disabled="loading"
        class="btn-conntect ml-auto"
        size="small"
        :title="t('label.connect')"
        data-testid="settings-calendar-connect-calendar-btn"
      >
        <template v-slot:icon>
          <icon-arrow-right class="size-3 stroke-3"/>
        </template>
        {{ t('label.connectCalendar') }}
      </primary-button>
      <primary-button
        v-if="type === CalendarManagementType.Edit"
        @click="emit('modify', cal.id)"
        :disabled="loading"
        class="btn-edit ml-auto"
        size="small"
        :title="t('label.edit')"
        data-testid="settings-calendar-edit-calendar-btn"
      >
        <template v-slot:icon>
          <icon-pencil class="size-3 stroke-3"/>
        </template>
        {{ t('label.editCalendar') }}
      </primary-button>
      <button
        v-if="!cal.connected"
        class="btn-remove bg-transparent p-0.5 disabled:scale-100 disabled:opacity-50 disabled:shadow-none"
        :disabled="loading"
        @click="emit('remove', cal.id)"
        :title="t('label.remove')"
        data-testid="settings-calendar-remove-calendar-btn"
      >
        <icon-x class="size-5 stroke-red-500 stroke-2"/>
      </button>
    </div>
  </div>
</template>
