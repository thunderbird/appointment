<script setup lang="ts">
import type { Dayjs } from 'dayjs';
import { computed, inject, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { PhCaretLeft, PhCaretRight } from '@phosphor-icons/vue';
import { useAppointmentStore } from '@/stores/appointment-store';
import { dayjsKey } from '@/keys';
import { BookingsFilterOptions } from '@/definitions';
import { Appointment } from '@/models';
import { VisualDivider } from '@thunderbirdops/services-ui';
import MeetingDateAppointmentItem from './MeetingDateAppointmentItem.vue';
import { isUnconfirmed } from '@/utils';

interface Props {
  filter: BookingsFilterOptions,
}
const props = withDefaults(defineProps<Props>(), {
  filter: BookingsFilterOptions.All,
});

const dj = inject(dayjsKey);
const appointmentStore = useAppointmentStore();
const { appointments } = storeToRefs(appointmentStore);

const selectedMonth = ref<Dayjs>(dj());
const monthlyAppointments = computed(() => {
  return appointments.value.filter((appointment) => {
    return dj(appointment.slots[0].start).isSame(selectedMonth.value, 'month');
  });
});

const groupedAppointments = computed(() => {
  const groups: Record<string, Appointment[]> = {};
  monthlyAppointments.value.forEach((appointment) => {
    const dayKey = dj(appointment.slots[0].start).format('YYYY-MM-DD');
    if (!groups[dayKey]) groups[dayKey] = [];
    groups[dayKey].push(appointment);
  });

  return Object.entries(groups)
    .sort(([a], [b]) => dj(a).valueOf() - dj(b).valueOf())
    .map(([day, appts]) => ({
      day,
      label: dj(day).format('dddd, MMM D'),
      appointments: appts
        .filter((a) => props.filter === BookingsFilterOptions.Unconfirmed ? isUnconfirmed(a) : true)
        .sort((a, b) => dj(a.slots[0].start).valueOf() - dj(b.slots[0].start).valueOf()),
    }));
});
</script>

<template>
  <div class="month-picker">
    <button @click="selectedMonth = selectedMonth.subtract(1, 'month')">
      <ph-caret-left size="24" />
    </button>
  
    <h1>{{ selectedMonth.format('MMMM YYYY') }}</h1>
  
    <button @click="selectedMonth = selectedMonth.add(1, 'month')">
      <ph-caret-right size="24" />
    </button>
  </div>

  <visual-divider class="divider" />

  <template v-for="group in groupedAppointments" :key="group.day">
    <template v-if="group.appointments.length > 0">
      <h2>{{ group.label }}</h2>
      <div class="item-container">
        <meeting-date-appointment-item
          v-for="monthlyAppt in group.appointments" :key="monthlyAppt.id"
          :name="monthlyAppt.slots[0].attendee.name"
          :email="monthlyAppt.slots[0].attendee.email"
          :startTime="(monthlyAppt.slots[0].start as string)"
          :duration="monthlyAppt.slots[0].duration"
          :needs-confirmation="isUnconfirmed(monthlyAppt)"
        />
      </div>
    </template>
  </template>
</template>

<style scoped>
h1 {
  font-size: 1.5rem;
  font-family: metropolis;
  font-weight: 500;
  text-align: center;
}

h2 {
  font-size: 1rem;
  color: var(--colour-ti-secondary);
  text-align: center;
  margin-block-start: 0.875rem;
  margin-block-end: 0.625rem;
}

.divider {
  margin-block: 0.875rem;
}

.month-picker {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.item-container {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
</style>
