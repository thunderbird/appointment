<script setup lang="ts">
import { inject, computed, toRefs } from 'vue';
import { useI18n } from 'vue-i18n';
import { timeFormat } from '@/utils';
import { CalendarEvent } from '@/models';

// icons
import {
  PhCalendarBlank,
  PhClock,
  PhUsers,
} from '@phosphor-icons/vue';
import { dayjsKey } from '@/keys';

// component constants
const { t } = useI18n();
const dj = inject(dayjsKey);

// component properties
interface Props {
  event?: CalendarEvent, // event to show details in popup for
  position?: string, // Popup position relative to the trigger element
}
const props = defineProps<Props>();

const { event } = toRefs(props);

// format datetime of event
const eventDateTime = computed(
  () => {
    const dateTimeParts = [];
    if (props.event) {
      // calculate date for active event
      const start = dj(props.event.time.start);
      dateTimeParts.push(start.format('dddd L'));
      if (!props.event.customData.all_day) {
        // add time if it's not an all day event
        const end = dj(props.event.time.end);
        dateTimeParts.push(start.format(`, ${timeFormat()} - `));
        dateTimeParts.push(end.format(timeFormat()));
      }
    }
    return dateTimeParts.join('');
  },
);
</script>

<template>
  <div
    class="event-popup"
    :class="{
      'position-left': position === 'left',
      'position-top': position === 'top'
    }"
  >
    <div
      class="popup-arrow"
      :class="{
        'arrow-right': !position || position === 'right',
        'arrow-left': position === 'left',
        'arrow-top': position === 'top',
      }"
    ></div>
    <div class="popup-content">
      <div class="event-title">{{ event?.title }}</div>
      <div class="event-detail">
        <ph-clock class="detail-icon" />
        {{ eventDateTime }}
      </div>
      <div class="event-detail">
        <ph-calendar-blank class="detail-icon" />
        {{ event?.customData?.calendar_title }}
      </div>
      <div v-if="event?.customData?.attendee" class="event-detail">
        <ph-users class="detail-icon" />
        {{ t('label.guest', { 'count': 1 }) }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.event-popup {
  position: absolute;
  z-index: 30;
  transform: translateY(-50%);
  border-radius: 0.375rem;
  background-color: var(--colour-neutral-base);
  padding: 0.75rem;
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  transition: all 0.15s ease;

  &.position-left {
    transform: translateX(-100%) translateY(-50%);
  }

  &.position-top {
    transform: translateX(-50%) translateY(-100%);
  }
}

.popup-arrow {
  position: absolute;
  width: 0.75rem;
  height: 0.75rem;
  transform: rotate(45deg);
  background-color: var(--colour-neutral-base);

  &.arrow-right {
    left: -0.375rem;
    top: 50%;
    transform: translateY(-50%) rotate(45deg);
  }

  &.arrow-left {
    right: -0.375rem;
    top: 50%;
    transform: translateY(-50%) rotate(45deg);
  }

  &.arrow-top {
    bottom: -0.375rem;
    left: 50%;
    transform: translateX(-50%) rotate(45deg);
  }
}

.popup-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  color: var(--colour-ti-base);
}

.event-title {
  max-width: 24rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--colour-primary-default);
}

.event-detail {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
}

.detail-icon {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
  color: var(--colour-primary-default);
}
</style>
