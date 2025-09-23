<script setup lang="ts">
import { computed, inject } from 'vue';
import { timeFormat } from '@/utils';
import { IconNotes } from '@tabler/icons-vue';
import { PhClock, PhCalendarBlank, PhVideoCamera } from '@phosphor-icons/vue'
import { useI18n } from 'vue-i18n';
import { Appointment } from '@/models';
import { dayjsKey } from '@/keys';
import { UserAvatar, VisualDivider } from '@thunderbirdops/services-ui';
import { useUserStore } from '@/stores/user-store';

interface Props {
  appointment: Appointment | null;
}
const props = defineProps<Props>();

const dj = inject(dayjsKey);
const { t } = useI18n();
const user = useUserStore();

const meetingLinkURL = computed(() => props.appointment?.slots[0].meeting_link_url);
const attendeesSlots = computed(() => props.appointment.slots.filter((s) => s.attendee));
</script>

<template>
  <div class="appointment-content">
    <div class="time-slots">
      <template v-for="s in appointment.slots" :key="s.start">
        <div class="time-slot">
          <ph-clock class="time-icon" weight="duotone" :aria-label="t('label.timeOfTheEvent')" />
          <div class="time-details">
            <p class="date">{{ dj(s.start).format('LL') }}</p>
            <div class="time-range">
              {{ dj(s.start).format(timeFormat()) }} - {{ dj(s.start).add(s.duration, 'minutes').format(timeFormat()) }}
              ({{ dj.duration(s.duration, 'minutes').humanize() }})
            </div>
          </div>
        </div>
      </template>
    </div>

    <div class="appointment-info">
      <ph-calendar-blank class="icon" />
      <span class="info-label">
        {{ t('label.calendar') }}
      </span>
      <span>
        {{ appointment.calendar_title }}
      </span>

      <ph-video-camera class="icon" />
      <span class="info-label">
        {{ t('label.videoLink') }}
      </span>
      <a v-if="meetingLinkURL" :href="meetingLinkURL" class="video-link" target="_blank">
        {{ meetingLinkURL }}
      </a>
      <span v-else>
        {{ t('label.notProvided') }}
      </span>
    </div>

    <VisualDivider />

    <div class="attendees-section">
      <div class="attendees-header">
        {{ t('label.attendees') }}
      </div>
      <div class="attendees-content">
        <div class="attendee-item">
          <UserAvatar :avatar-url="user.data.avatarUrl" :username="user.data.username" size="small" />
          {{ user.data.username }} ({{ t('label.host') }})
        </div>
        <template v-for="s in attendeesSlots" :key="s.start">
          <div class="attendee-item">
            <UserAvatar :username="s.attendee.email" size="small" />
            {{ s.attendee.email }}
          </div>
        </template>
      </div>
    </div>

    <VisualDivider />

    <div v-if="appointment.details" class="notes-section">
      <div class="notes-header">
        <icon-notes class="notes-icon" />
        {{ t('label.notes') }}
      </div>
      <div class="notes-content">{{ appointment.details }}</div>
    </div>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.appointment-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin-block-end: 2rem;
  color: var(--colour-ti-secondary);
}

/* Status labels */
.status-label {
  margin-bottom: 1.5rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-confirmed {
  color: var(--colour-ti-success);
}

.status-requested {
  color: var(--colour-ti-warning);
}

.status-unconfirmed {
  color: var(--colour-ti-critical);
}

.status-modified {
  color: var(--colour-warning-default);
}

/* Status labels */
.status-label {
  margin-bottom: 1.5rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-confirmed {
  color: var(--colour-ti-success);
}

.status-requested {
  color: var(--colour-ti-warning);
}

.status-unconfirmed {
  color: var(--colour-ti-critical);
}

/* Time slots section */
.time-slots {
  width: 100%;
  padding: 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  background-color: var(--colour-neutral-lower);
}

.time-slot {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.time-icon {
  width: 2.5rem;
  height: 2.5rem;
  padding: 0.5rem;
  background-color: color-mix(in srgb, var(--colour-ti-highlight) 20%, transparent);
  border-radius: 9999px;
  flex-shrink: 0;
}

.time-details .date {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.32;
}

.time-range {
  margin-top: 0.25rem;
  font-size: 0.8125rem;
  color: var(--colour-ti-secondary);
}

/* Appointment info section */
.appointment-info {
  display: grid;
  grid-template-columns: 1.5rem minmax(auto-fit, 116px) 1fr;
  align-items: center;
  row-gap: 0.75rem;
  column-gap: 0.5rem;
  font-size: 1rem;

  .icon {
    width: 1.5rem;
    height: 1.5rem;
    color: var(--colour-ti-highlight);
  }
}

.info-row {
  margin-bottom: 0.75rem;
}

.info-label {
  font-weight: 600;
  font-size: 1rem;
}

.video-link {
  color: var(--colour-accent-teal);
  text-decoration: underline;
  text-underline-offset: 2px;

  &:hover {
    color: var(--colour-apmt-primary);
  }
}

/* Attendees section */
.attendees-section {
  width: max-content;
  max-width: 100%;
  font-size: 1rem;
}

.attendees-header {
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.attendees-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.attendee-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;

  & :first-child {
    flex-shrink: 0;
  }  
}

/* Notes section */
.notes-section {
  width: 100%;
  padding-left: 1rem;
  font-size: 0.875rem;
}

.notes-header {
  margin-bottom: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.notes-icon {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
  fill: transparent;
  stroke: var(--colour-ti-muted);
  stroke-width: 2;
}

.notes-content {
  border-radius: 0.5rem;
  border: 1px solid var(--colour-neutral-border);
  padding: 1rem;
}

.dark .notes-content {
  border-color: var(--colour-neutral-border);
}

@media (--md) {
  .appointment-info {
    grid-template-columns: 1.5rem minmax(auto, 100px) 1fr;
  }
}
</style>