<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import { PhClock, PhMapPin } from '@phosphor-icons/vue';
import { useBookingViewStore } from '@/stores/booking-view-store';

const { t } = useI18n();
const calendarStore = useBookingViewStore();

const { appointment } = storeToRefs(calendarStore);

console.log(appointment.value);
</script>

<template>
  <div class="booking-header">
    <div class="booking-header-title-container">
      <h2 data-testid="booking-view-book-a-time-to-meet-with-text">
        {{ t('text.bookATimeToMeetWith', { name: appointment.owner_name }) }}
      </h2>

      <div class="booking-header-time-place">
        <div class="booking-header-time-place-item">
          <ph-clock size="16" />
          <span>{{ appointment.slot_duration }} minutes</span>
        </div>
        <div class="booking-header-time-place-item">
          <ph-map-pin size="16" />
          <span>Online meeting</span>
        </div>
      </div>
    </div>

    <strong data-testid="booking-view-title-text">{{ appointment.title }}</strong>
    <p v-if="appointment.details">{{ appointment.details }}</p>
  </div>
</template>

<style scoped>
.booking-header {
  margin-block-end: 2rem;
  font-family: Inter, sans-serif;

  p, strong {
    line-height: 1.32;
    color: var(--colour-ti-base);
  }

  strong {
    font-weight: 700;
  }

  .booking-header-title-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: calc(100% - 370px); /* Aligns with the slot-selection-aside width */
    margin-block-end: 1rem;

    h2 {
      font-size: 1.5rem;
      font-weight: 400;
      color: var(--colour-ti-highlight);
    }

    .booking-header-time-place {
      display: flex;
      align-items: center;
      gap: 2rem;

      .booking-header-time-place-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.875rem;
        color: var(--colour-ti-base);
      }
    }
  }
}
</style>