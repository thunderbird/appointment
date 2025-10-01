<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { useAppointmentStore } from '@/stores/appointment-store';
import { VisualDivider } from '@thunderbirdops/services-ui';
import { BookingStatus } from '@/definitions';
import DateRequestedAppointmentItem from './DateRequestedAppointmentItem.vue';

const { t } = useI18n();

const appointmentStore = useAppointmentStore();
const { appointmentsSortedByDateRequested } = storeToRefs(appointmentStore);
</script>

<template>
  <!-- Today -->
  <template v-if="appointmentsSortedByDateRequested.today.length > 0">
    <h2>{{ t('label.today') }}</h2>
  
    <visual-divider />

    <date-requested-appointment-item
      v-for="todayAppt in appointmentsSortedByDateRequested.today"
      :key="todayAppt.id"
      :name="todayAppt.slots[0].attendee.name"
      :email="todayAppt.slots[0].attendee.email"
      :request-date="todayAppt.time_created"
      :meeting-date="todayAppt.slots[0].start as string"
      :needs-confirmation="todayAppt.slots[0].booking_status === BookingStatus.Requested"
    />
  </template>

  <!-- This week -->
  <template v-if="appointmentsSortedByDateRequested.thisWeek.length > 0">
    <h2>{{ t('label.thisWeek') }}</h2>
  
    <visual-divider />

    <date-requested-appointment-item
      v-for="weekAppt in appointmentsSortedByDateRequested.thisWeek"
      :key="weekAppt.id"
      :name="weekAppt.slots[0].attendee.name"
      :email="weekAppt.slots[0].attendee.email"
      :request-date="weekAppt.time_created"
      :meeting-date="weekAppt.slots[0].start as string"
      :needs-confirmation="weekAppt.slots[0].booking_status === BookingStatus.Requested"
    />
  </template>

  <!-- This month -->
  <template v-if="appointmentsSortedByDateRequested.thisMonth.length > 0">
    <h2>{{ t('label.thisMonth') }}</h2>
  
    <visual-divider />

    <date-requested-appointment-item
      v-for="monthAppt in appointmentsSortedByDateRequested.thisMonth"
      :key="monthAppt.id"
      :name="monthAppt.slots[0].attendee.name"
      :email="monthAppt.slots[0].attendee.email"
      :request-date="monthAppt.time_created"
      :meeting-date="monthAppt.slots[0].start as string"
      :needs-confirmation="monthAppt.slots[0].booking_status === BookingStatus.Requested"
    />
  </template>

  <!-- Earlier -->
  <template v-if="appointmentsSortedByDateRequested.earlier.length > 0">
    <h2>{{ t('label.earlier') }}</h2>
  
    <visual-divider />

    <date-requested-appointment-item
      v-for="earlierAppt in appointmentsSortedByDateRequested.earlier"
      :key="earlierAppt.id"
      :name="earlierAppt.slots[0].attendee.name"
      :email="earlierAppt.slots[0].attendee.email"
      :request-date="earlierAppt.time_created"
      :meeting-date="earlierAppt.slots[0].start as string"
      :needs-confirmation="earlierAppt.slots[0].booking_status === BookingStatus.Requested"
    />
  </template>
</template>

<style scoped>
h2 {
  font-size: 1.5rem;
  font-family: metropolis;
  text-align: center;
  margin-bottom: 0.5rem;
}
</style>
