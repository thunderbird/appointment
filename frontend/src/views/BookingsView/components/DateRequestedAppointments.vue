<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { useAppointmentStore } from '@/stores/appointment-store';
import { VisualDivider } from '@thunderbirdops/services-ui';
import { BookingsFilterOptions, BookingStatus } from '@/definitions';
import DateRequestedAppointmentItem from './DateRequestedAppointmentItem.vue';
import { isUnconfirmed } from '@/utils';

interface Props {
  filter: BookingsFilterOptions,
}
const props = withDefaults(defineProps<Props>(), {
  filter: BookingsFilterOptions.All,
});

const { t } = useI18n();

const appointmentStore = useAppointmentStore();
const { appointmentsSortedByDateRequested } = storeToRefs(appointmentStore);


const filteredAppointments = computed(() => {
  if (props.filter === BookingsFilterOptions.All) {
    return appointmentsSortedByDateRequested.value;
  }
  if (props.filter === BookingsFilterOptions.Unconfirmed) {
    return {
      today: appointmentsSortedByDateRequested.value.today.filter((a) => isUnconfirmed(a)),
      thisWeek: appointmentsSortedByDateRequested.value.thisWeek.filter((a) => isUnconfirmed(a)),
      thisMonth: appointmentsSortedByDateRequested.value.thisMonth.filter((a) => isUnconfirmed(a)),
      earlier: appointmentsSortedByDateRequested.value.earlier.filter((a) => isUnconfirmed(a)),
    };
  }
});
</script>

<template>
  <!-- Today -->
  <template v-if="filteredAppointments.today.length > 0">
    <h2>{{ t('label.today') }}</h2>
  
    <visual-divider />

    <div class="item-container">
      <date-requested-appointment-item
        v-for="todayAppt in filteredAppointments.today"
        :key="todayAppt.id"
        :name="todayAppt.slots[0].attendee.name"
        :email="todayAppt.slots[0].attendee.email"
        :request-date="todayAppt.time_created"
        :meeting-date="(todayAppt.slots[0].start as string)"
        :needs-confirmation="isUnconfirmed(todayAppt)"
      />
    </div>
  </template>

  <!-- This week -->
  <template v-if="filteredAppointments.thisWeek.length > 0">
    <h2>{{ t('label.thisWeek') }}</h2>
  
    <div class="item-container">
      <date-requested-appointment-item
        v-for="weekAppt in filteredAppointments.thisWeek"
        :key="weekAppt.id"
        :name="weekAppt.slots[0].attendee.name"
        :email="weekAppt.slots[0].attendee.email"
        :request-date="weekAppt.time_created"
        :meeting-date="(weekAppt.slots[0].start as string)"
        :needs-confirmation="isUnconfirmed(weekAppt)"
      />
    </div>
  </template>

  <!-- This month -->
  <template v-if="filteredAppointments.thisMonth.length > 0">
    <h2>{{ t('label.thisMonth') }}</h2>
  
    <div class="item-container">
      <date-requested-appointment-item
        v-for="monthAppt in filteredAppointments.thisMonth"
        :key="monthAppt.id"
        :name="monthAppt.slots[0].attendee.name"
        :email="monthAppt.slots[0].attendee.email"
        :request-date="monthAppt.time_created"
        :meeting-date="(monthAppt.slots[0].start as string)"
        :needs-confirmation="isUnconfirmed(monthAppt)"
      />
    </div>
  </template>

  <!-- Earlier -->
  <template v-if="filteredAppointments.earlier.length > 0">
    <h2>{{ t('label.earlier') }}</h2>
  
    <div class="item-container">
      <date-requested-appointment-item
        v-for="earlierAppt in filteredAppointments.earlier"
        :key="earlierAppt.id"
        :name="earlierAppt.slots[0].attendee.name"
        :email="earlierAppt.slots[0].attendee.email"
        :request-date="earlierAppt.time_created"
        :meeting-date="(earlierAppt.slots[0].start as string)"
        :needs-confirmation="isUnconfirmed(earlierAppt)"
      />
    </div>
  </template>
</template>

<style scoped>
h2 {
  font-size: 1.5rem;
  font-family: metropolis;
  text-align: center;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}

.divider {
  margin-block: 0.875rem 0.375rem;
}

.item-container {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
</style>
