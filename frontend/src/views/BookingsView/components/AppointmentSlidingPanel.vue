<script setup lang="ts">
import { BookingStatus } from '@/definitions';
import { computed, inject, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { Appointment } from '@/models';
import SlidingPanel from '@/elements/SlidingPanel.vue';
import { PrimaryButton, DangerButton } from '@thunderbirdops/services-ui';
import { useUserStore } from '@/stores/user-store';
import { useAppointmentStore } from '@/stores/appointment-store';
import { dayjsKey } from '@/keys';
import { APPOINTMENT_SLIDING_PANEL_STEPS } from '../constants';

// Panel Steps
import AppointmentSlidingPanelConfirmation from './AppointmentSlidingPanelConfirmation.vue';
import AppointmentSlidingPanelDetails from './AppointmentSlidingPanelDetails.vue';

const user = useUserStore();
const apmtStore = useAppointmentStore();

// component emits
const emit = defineEmits(['close']);

// component constants
const { t } = useI18n();
const dj = inject(dayjsKey);

interface Props {
  appointment: Appointment | null;
}
const props = defineProps<Props>();

const cancelReason = ref<string>('');
const isAppointmentConfirmed = ref<boolean>();
const panelRef = ref<InstanceType<typeof SlidingPanel>>()
const panelStep = ref<APPOINTMENT_SLIDING_PANEL_STEPS>(APPOINTMENT_SLIDING_PANEL_STEPS.DETAILS);

// computed properties
const status = computed(() => props.appointment?.slots[0].booking_status);
const isExpired = computed(() => {
  return props.appointment?.slots.reduce((p, c) => dj.max(p, dj(c.start).add(c.duration, 'minutes')), dj('1970-01-01')) < dj();
});
const isPast = computed(() => props.appointment?.slots[0].start < dj());

// methods
const closePanel = () => {
  panelRef.value?.closePanel();
  emit('close');
}

const confirmAppointment = (isConfirmed: boolean) => {
  isAppointmentConfirmed.value = isConfirmed
  panelStep.value = APPOINTMENT_SLIDING_PANEL_STEPS.CONFIRMATION
};

const deleteAppointment = () => {
  apmtStore.deleteAppointment(props.appointment?.id);
  closePanel();
};

const cancelAppointment = () => {
  apmtStore.cancelAppointment(props.appointment?.id, cancelReason.value);
  cancelReason.value = '';
  closePanel();
};

defineExpose({
  showPanel: () => {
    panelRef.value?.showPanel();
  }
})
</script>

<template>
  <sliding-panel
    ref="panelRef"
    :title="appointment?.title"
    @close="emit('close')"
  >
    <appointment-sliding-panel-details
      v-if="appointment && panelStep === APPOINTMENT_SLIDING_PANEL_STEPS.DETAILS"
      :appointment="appointment"
      :cancelReason="cancelReason"
      @update:cancelReason="cancelReason = $event"
    />

    <appointment-sliding-panel-confirmation
      v-if="appointment && panelStep === APPOINTMENT_SLIDING_PANEL_STEPS.CONFIRMATION"
      :signedUrl="user.data.signedUrl"
      :slotId="props.appointment.slots[0].id"
      :slotToken="props.appointment.slots[0].booking_tkn"
      :confirmed="isAppointmentConfirmed"
      @close="closePanel"
    />

    <!-- CTA buttons for APPOINTMENT_SLIDING_PANEL_STEPS.DETAILS -->
    <template #cta v-if="panelStep === APPOINTMENT_SLIDING_PANEL_STEPS.DETAILS">
      <div v-if="status === BookingStatus.Booked && !isPast" class="cta-single">
        <danger-button 
          data-testid="appointment-modal-cancel-btn" 
          @click="cancelAppointment()" 
          :title="t('label.cancel')"
        >
          {{ t('label.cancelBooking') }}
        </danger-button>
      </div>
      <div v-else-if="isExpired" class="cta-single">
        <danger-button 
          class="btn-deny" 
          @click="deleteAppointment()" 
          :title="t('label.delete')"
        >
          {{ t('label.deleteBooking') }}
        </danger-button>
      </div>
      <div v-else-if="status === BookingStatus.Requested" class="cta-dual">
        <primary-button 
          class="btn-confirm" 
          @click="confirmAppointment(true)"
          :title="t('label.confirm')"
        >
          {{ t('label.confirmBooking') }}
        </primary-button>
        <danger-button 
          class="btn-deny" 
          @click="confirmAppointment(false)"
          :title="t('label.deny')"
        >
          {{ t('label.denyBooking') }}
        </danger-button>
      </div>
    </template>
  </sliding-panel>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

/* CTA buttons for APPOINTMENT_SLIDING_PANEL_STEPS.DETAILS */
.cta-single {
  display: flex;
  justify-content: flex-end;

  .btn-confirm {
    flex-grow: 1;
  }

  .btn-deny {
    flex-grow: 1;
  }
}

.cta-dual {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  flex-wrap: wrap;
}

.cta-single, .cta-dual {
  .btn-confirm {
    flex-grow: 1;
  }

  .btn-deny {
    flex-grow: 1;
  }
}

@media (--sm) {
  .cta-dual, .cta-single {
    .btn-confirm {
      flex-grow: 0;
    }

    .btn-deny {
      flex-grow: 0;
    }
  }
}
</style> 
