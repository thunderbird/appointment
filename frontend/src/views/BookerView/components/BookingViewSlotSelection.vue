<script setup lang="ts">
import { computed, inject } from 'vue';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import {
  IconWorld,
  IconCalendarClock,
  IconCalendar,
  IconClock,
  IconCircleCheckFilled,
  IconMapPin
} from '@tabler/icons-vue';
import { PrimaryButton } from '@thunderbirdops/services-ui';

import { useBookingViewStore } from '@/stores/booking-view-store';
import { useScheduleStore } from '@/stores/schedule-store';
import { DateFormatStrings } from '@/definitions';
import { Slot } from '@/models';
import { dayjsKey } from '@/keys';

import CalendarQalendar from '@/components/CalendarQalendar.vue';

const { t } = useI18n();
const { activeSchedules } = storeToRefs(useScheduleStore());
const { appointment, activeDate, selectedEvent } = storeToRefs(useBookingViewStore());
const dj = inject(dayjsKey);

const emit = defineEmits(['openModal']);

// component properties
interface Props {
  showNavigation: boolean,
}
defineProps<Props>();

const timezone = computed(() => dj.tz.guess());
const selectedSlotDate = computed(() => dj(selectedEvent.value?.start).format('LL'))
const selectedSlotTimeDuration = computed(() => {
  const startTime = dj(selectedEvent.value?.start).format('LT');
  const endTime = dj(selectedEvent.value?.start)
    .add(selectedEvent.value?.slot_duration, 'minutes')
    .format('LT');

  return `${startTime} ${t('label.to')} ${endTime}`;
})


/**
 * Select a specific time slot
 * @param day string
 */
const selectEvent = (day: string) => {
  // set event selected
  for (let i = 0; i < appointment.value.slots.length; i += 1) {
    const slot: Slot = appointment.value.slots[i];
    if (dj(slot.start).format(DateFormatStrings.Qalendar) === day) {
      slot.selected = true;
      const e = { ...appointment.value, ...slot };
      delete e.slots;
      selectedEvent.value = e;
    } else {
      slot.selected = false;
    }
  }
};

</script>

<template>
  <div v-if="appointment" class="booker-view-container">
    <calendar-qalendar
      class="w-full"
      :current-date="activeDate"
      :appointments="[appointment]"
      :is-booking-route="true"
      :fixed-duration="activeSchedules[0]?.slot_duration"
      @event-selected="selectEvent"
      data-testid="booking-view-calendar-div"
    >
    </calendar-qalendar>

    <aside>
      <p class="invitation-text" data-testid="booking-view-inviting-you-text">
        {{ t('text.nameIsInvitingYou', { name: appointment.owner_name }) }}
      </p>
      <h1 class="appointment-title" data-testid="booking-view-title-text">
        {{ appointment.title }}
      </h1>
      <p v-if="appointment.details" class="appointment-details">
        {{ appointment.details }}
      </p>
      <div class="timezone-section">
        <span class="timezone-label">{{ t('label.timeZone') }}:</span>
        <div class="timezone-display">
          <icon-world size="24" />
          {{ timezone }}
        </div>
      </div>

      <div v-if="selectedEvent" class="appointment-card">
        <h3>Booking Details</h3>
        <div class="appointment-card-inner">
          <header>
            {{ selectedEvent.title }}
            <icon-circle-check-filled size="24"/>
          </header>
          <div class="appointment-card-inner-details">
            <icon-calendar size="16"/>
            <span>{{ selectedSlotDate }}</span>
            <icon-map-pin size="16"/>
            <!-- TODO: We are currently only allowing for events to be online but the backend defaults to in person -->
            <!-- <span>{{ selectedEvent.location_type === EventLocationType.Online ? t('label.virtual') : t('label.inPerson') }}</span> -->
            <span>{{ t('label.virtual') }}</span>
            <icon-clock size="16"/>
            <span>{{ selectedSlotTimeDuration }} <span class="timezone-badge">{{ timezone }}</span></span>
            <icon-clock size="16"/>
            <span>{{ t('units.minutes', { value: selectedEvent.slot_duration }) }}</span>
          </div>
        </div>
      </div>

      <div v-else class="appointment-card empty">
        Select a time from the calendar
        <icon-calendar-clock size="108"/>
      </div>

      <primary-button
        :label="t('label.confirmSelection')"
        :disabled="!selectedEvent"
        @click="emit('openModal')"
        :title="t('label.confirm')"
        class="confirm-selection-button"
        data-testid="booking-view-confirm-selection-button"
      >
        {{ t('label.confirmSelection') }}
      </primary-button>
    </aside>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.booker-view-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;

  aside {
    .invitation-text {
      margin-bottom: 0.825rem;
      font-size: 0.825rem;
      font-weight: 600;
      color: var(--colour-ti-muted);
    }

    .appointment-title {
      margin-bottom: 0.825rem;
      font-size: 1.725rem;
      line-height: 2.25rem;
      color: var(--colour-ti-base);
    }

    .appointment-details {
      margin-bottom: 1.5rem;
      color: var(--colour-ti-base);
    }

    .timezone-section {
      margin-bottom: 1.5rem;
      display: flex;
      flex-direction: row;
      align-items: center;
      gap: 1rem;

      .timezone-label {
        font-size: 0.875rem;
        line-height: 1.75rem;
        color: var(--colour-ti-base);
      }

      .timezone-display {
        font-size: 0.875rem;
        line-height: 1.25rem;
        color: var(--colour-accent-teal);
        display: flex;
        align-items: center;
        gap: 0.5rem;
      }
    }

    .appointment-card {
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 1rem;
      padding: 1rem 0.5rem;
      border: 1px dashed var(--colour-neutral-border);
      border-radius: 0.25rem;
      background-color: var(--colour-neutral-raised);

      &.empty {
        align-items: center;
        padding: 4rem 1.5rem;
      }

      h3 {
        text-align: center;
        font-weight: 500;
      }

      .appointment-card-inner {
        padding: 1rem 1.5rem;
        border-radius: 0.25rem;
        color: var(--colour-ti-base);
        /* TODO: Color not in design system */
        background-color: #7d9cfb;

        header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-block-end: 1rem;
        }

        .appointment-card-inner-details {
          display: grid;
          grid-template-columns: 1.5rem 1fr;
          align-items: center;
          row-gap: 0.25rem;
          column-gap: 0.125rem;

          .timezone-badge {
            background-color: var(--colour-neutral-raised);
            font-size: 0.75rem;
            padding: 0.25rem 0.375rem;
            margin-inline-start: 0.25rem;
            border-radius: 8px;
          }
        }
      }
    }

    .confirm-selection-button {
      margin-inline-start: auto;
      margin-block-start: 1rem;
    }
  }
}

@media (--md) {
  .booker-view-container {
    flex-direction: row;

    aside {
      width: 470px;

      .timezone-section {
        flex-direction: row;
      }
    }
  }
}

</style>