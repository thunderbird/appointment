<script setup lang="ts">
import { BookingStatus } from '@/definitions';
import { computed, inject, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { Appointment } from '@/models';
import SlidingPanel from '@/elements/SlidingPanel.vue';
import { PrimaryButton, DangerButton, TextInput, LinkButton } from '@thunderbirdops/services-ui';
import { useUserStore } from '@/stores/user-store';
import { useAppointmentStore } from '@/stores/appointment-store';
import { dayjsKey } from '@/keys';
import { APPOINTMENT_SLIDING_PANEL_STEPS } from '../constants';

// Panel Steps
import AppointmentSlidingPanelBookingConfirmation from './AppointmentSlidingPanelBookingConfirmation.vue';
import AppointmentSlidingPanelDetails from './AppointmentSlidingPanelDetails.vue';
import AppointmentSlidingPanelModify, { ModifyFormData } from './AppointmentSlidingPanelModify.vue';
import AppointmentSlidingPanelCancel from './AppointmentSlidingPanelCancel.vue';

const { t } = useI18n();
const dj = inject(dayjsKey);
const user = useUserStore();
const apmtStore = useAppointmentStore();

const emit = defineEmits(['close']);
const props = defineProps<{
  appointment: Appointment | null;
}>();

const panelRef = ref<InstanceType<typeof SlidingPanel>>()
const panelStep = ref<APPOINTMENT_SLIDING_PANEL_STEPS>(APPOINTMENT_SLIDING_PANEL_STEPS.DETAILS);
const modifyPanelRef = ref<InstanceType<typeof AppointmentSlidingPanelModify>>();

const appointmentTitle = ref<string>('');
const modifyFormData = ref<ModifyFormData>();
const hideModifyFieldsAndCTA = ref<boolean>(false);
const isAppointmentConfirmed = ref<boolean>();

// computed properties
const status = computed(() => props.appointment?.slots[0].booking_status);
const isExpired = computed(() => {
  return props.appointment?.slots.reduce((p, c) => dj.max(p, dj(c.start).add(c.duration, 'minutes')), dj('1970-01-01')) < dj();
});
const isPast = computed(() => props.appointment?.slots[0].start < dj());

// methods
const closePanel = () => {
  resetPanelState();

  // Close SlidingPanel component
  panelRef.value.closePanel()

  // Emit close event for the Bookings View to cleanup its state
  emit('close')
}

const resetPanelState = () => {
  panelStep.value = APPOINTMENT_SLIDING_PANEL_STEPS.DETAILS;
  hideModifyFieldsAndCTA.value = false;
}

const moveToConfirmAppointmentStep = (isConfirmed: boolean) => {
  isAppointmentConfirmed.value = isConfirmed
  panelStep.value = APPOINTMENT_SLIDING_PANEL_STEPS.CONFIRMATION
};

const deleteAppointment = () => {
  apmtStore.deleteAppointment(props.appointment?.id);
  closePanel();
};

const moveToCancelAppointmentStep = () => {
  panelStep.value = APPOINTMENT_SLIDING_PANEL_STEPS.CANCEL
};

const moveToModifyAppointmentStep = () => {
  appointmentTitle.value = props.appointment?.title || '';
  modifyFormData.value = { notes: '' };

  panelStep.value = APPOINTMENT_SLIDING_PANEL_STEPS.MODIFY
}

const modifyAppointmentStepSaveClicked = () => {
  modifyPanelRef.value?.handleModifyFormSubmit();
}

const moveToDetailsStep = () => {
  panelStep.value = APPOINTMENT_SLIDING_PANEL_STEPS.DETAILS
}

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
    @close="() => { resetPanelState(); emit('close')}"
  >
    <!-- Title (only editable in step MODIFY) -->
    <template #title v-if="appointment && panelStep === APPOINTMENT_SLIDING_PANEL_STEPS.MODIFY && !hideModifyFieldsAndCTA">
      <text-input
        name="appointmentTitle"
        v-model="appointmentTitle"
        :placeholder="appointment.title"
      />
    </template>

    <!-- Content (each panel step with respective props) -->
    <template v-if="appointment">
      <appointment-sliding-panel-details
        v-if="panelStep === APPOINTMENT_SLIDING_PANEL_STEPS.DETAILS"
        :appointment="appointment"
      />

      <appointment-sliding-panel-booking-confirmation
        v-else-if="panelStep === APPOINTMENT_SLIDING_PANEL_STEPS.CONFIRMATION"
        :signedUrl="user.data.signedUrl"
        :slotId="props.appointment.slots[0].id"
        :slotToken="props.appointment.slots[0].booking_tkn"
        :confirmed="isAppointmentConfirmed"
        @close="closePanel"
      />

      <appointment-sliding-panel-modify
        v-else-if="panelStep === APPOINTMENT_SLIDING_PANEL_STEPS.MODIFY"
        ref="modifyPanelRef"
        :appointment="appointment"
        :initialData="modifyFormData"
        :title="appointmentTitle"
        v-model:hideModifyFieldsAndCTA="hideModifyFieldsAndCTA"
        @close="closePanel"
      />

      <appointment-sliding-panel-cancel
        v-else-if="panelStep === APPOINTMENT_SLIDING_PANEL_STEPS.CANCEL"
        :appointment="appointment"
        @click:backButton="moveToDetailsStep()"
      />
    </template>

    <!-- CTA buttons for APPOINTMENT_SLIDING_PANEL_STEPS.DETAILS -->
    <template #cta v-if="panelStep === APPOINTMENT_SLIDING_PANEL_STEPS.DETAILS">
      <div v-if="status === BookingStatus.Booked && !isPast || status === BookingStatus.Modified" class="cta-single">
        <danger-button 
          data-testid="appointment-modal-modify-btn"
          @click="moveToModifyAppointmentStep()"
          :title="t('label.modify')"
        >
          {{ t('label.modifyBooking') }}
        </danger-button>
      </div>
      <div v-else-if="isExpired || status === BookingStatus.Cancelled || status === BookingStatus.Declined" class="cta-single">
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
          @click="moveToConfirmAppointmentStep(true)"
          :title="t('label.confirm')"
        >
          {{ t('label.confirmBooking') }}
        </primary-button>
        <danger-button 
          class="btn-deny" 
          @click="moveToConfirmAppointmentStep(false)"
          :title="t('label.deny')"
        >
          {{ t('label.denyBooking') }}
        </danger-button>
      </div>
    </template>

    <!-- CTA buttons for APPOINTMENT_SLIDING_PANEL_STEPS.MODIFY -->
    <template #cta v-else-if="panelStep === APPOINTMENT_SLIDING_PANEL_STEPS.MODIFY && !hideModifyFieldsAndCTA">
      <div class="cta-dual-spaced">
        <link-button
          class="cancel-btn"
          data-testid="appointment-modal-cancel-btn"
          @click="moveToCancelAppointmentStep()"
          :title="t('label.cancel')"
        >
          {{ t('label.cancelBooking') }}
        </link-button>

        <primary-button
          data-testid="appointment-modal-save-btn"
          :title="t('label.save')"
          @click="modifyAppointmentStepSaveClicked()"
        >
          {{ t('label.save') }}
        </primary-button>
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

/* CTA buttons for APPOINTMENT_SLIDING_PANEL_STEPS.MODIFY */
.cta-dual-spaced {
  display: flex;
  justify-content: space-between;

  .cancel-btn {
    color: var(--colour-danger-default);
  }
}
</style> 
