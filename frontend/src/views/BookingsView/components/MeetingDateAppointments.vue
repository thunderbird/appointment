<script setup lang="ts">
import type { Dayjs } from 'dayjs';
import { computed, inject, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { PhCaretLeft, PhCaretRight } from '@phosphor-icons/vue';
import { useAppointmentStore } from '@/stores/appointment-store';
import { dayjsKey } from '@/keys';
import { BookingStatus } from '@/definitions';
import MeetingDateAppointmentItem from './MeetingDateAppointmentItem.vue';
import { VisualDivider } from '@thunderbirdops/services-ui';

const dj = inject(dayjsKey);
const appointmentStore = useAppointmentStore();
const { appointments } = storeToRefs(appointmentStore);

const selectedMonth = ref<Dayjs>(dj());
const monthlyAppointments = computed(() => {
  return appointments.value.filter((appointment) => {
    return dj(appointment.slots[0].start).isSame(selectedMonth.value, 'month');
  });
});
</script>

<template>
  <div class="month-picker">
    <button @click="selectedMonth = selectedMonth.subtract(1, 'month')">
      <ph-caret-left />
    </button>
  
    {{ selectedMonth.format('MMMM YYYY') }}
  
    <button @click="selectedMonth = selectedMonth.add(1, 'month')">
      <ph-caret-right />
    </button>
  </div>

  <visual-divider />

  <template v-for="monthlyAppt in monthlyAppointments" :key="monthlyAppt.id">
    <meeting-date-appointment-item
      :name="monthlyAppt.slots[0].attendee.name"
      :email="monthlyAppt.slots[0].attendee.email"
      :startTime="monthlyAppt.slots[0].start as string"
      :duration="monthlyAppt.slots[0].duration"
      :needs-confirmation="monthlyAppt.slots[0].booking_status === BookingStatus.Requested"
    />
  </template>
</template>

<style scoped>
.month-picker {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>