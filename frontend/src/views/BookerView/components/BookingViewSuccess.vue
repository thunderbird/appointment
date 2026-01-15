<script setup lang="ts">
import { inject } from 'vue';
import { timeFormat } from '@/utils';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user-store';

import { LinkButton, PrimaryButton } from '@thunderbirdops/services-ui';
import { apiUrlKey, dayjsKey } from '@/keys';
import { Appointment, Attendee, Slot } from '@/models';
import { PhArrowRight, PhDownloadSimple, PhConfetti } from '@phosphor-icons/vue';

const { t } = useI18n();
const router = useRouter();

const dj = inject(dayjsKey);
const apiUrl = inject(apiUrlKey);
const user = useUserStore();

// component properties
interface Props {
  selectedEvent: Appointment & Slot,
  attendee: Attendee,
  requested: boolean, // True if we are requesting a booking, false if already confirmed
}
const props = defineProps<Props>();

const heading = props.requested
  ? t('info.bookingSuccessfullyRequested')
  : t('info.bookingSuccessfullyConfirmed');

const description = props.requested
  ? t('text.hostHasBeenNotified')
  : t('text.timeHasBeenConfirmed', {'email': props.attendee.email});

const date = dj(props.selectedEvent.start).format('ddd') + ', '
  + dj(props.selectedEvent.start).format('MMM DD') + ' from '
  + dj(props.selectedEvent.start).format(timeFormat()) + ' – '
  + dj(props.selectedEvent.start).add(props.selectedEvent.duration, 'minutes').format(timeFormat())
  + ' (' + dj.tz.guess() + ')';

const downloadUrl = `${apiUrl}/apmt/serve/ics/${props.selectedEvent.slug}/${props.selectedEvent.id}`;

</script>

<template>
  <div class="booking-success-container">
    <div class="booking-details">
      <div class="heading">
        <ph-confetti />
        {{ heading }}
      </div>
      <p>{{ description }}</p>
      <div class="info">
        <div class="logo">
          <img src="@/assets/svg/appointment_calendar_logo.svg" alt="Appointment Calendar Logo" />
        </div>
        <div>
          {{ date }}
          <br />
          {{ t('text.virtualMeetingWith', {name: attendee.name}) }}
        </div>
      </div>
      <div class="actions">
        <link-button :href="downloadUrl">
          <template #iconLeft>
            <ph-download-simple />
          </template>
          {{ t('label.downloadTheIcsFile') }}
        </link-button>
      </div>
    </div>
    <div class="appointment-call-out">
      <img src="@/assets/svg/appointment_logo.svg" alt="Appointment Logo" />
      <span class="tagline" v-text="t('app.tagline')"></span>
      <span class="description" v-text="t('app.description')"></span>
      <primary-button @click="router.push({ name: 'home' })">
        {{ user.authenticated ? t('label.dashboard') : t('label.subscribe') }}
        <template #iconRight>
          <ph-arrow-right weight="bold" />
        </template>
      </primary-button>
    </div>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.booking-success-container {
  display: flex;
  flex-direction: row;
  gap: 2rem;
}

.booking-details {
  border-radius: 1rem;
  padding: 2rem 1.5rem;
  max-width: 48rem;

  display: flex;
  flex-direction: column;
  gap: 1.5rem;

  background-color: var(--colour-neutral-base);
  font-family: Inter, sans-serif;

  .heading {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  
    color: var(--colour-ti-highlight);
    font-size: 1.5rem;
    text-transform: capitalize;
  
    svg {
      fill: var(--colour-ti-highlight);
    }
  }

  p {
    color: var(--colour-ti-base);
  }

  .info {
    display: flex;
    gap: 1.5rem;
    font-size: 1.25rem;
    color: var(--colour-ti-black);

    .logo {
      padding: 0.5rem;
      border-radius: 1rem;
      background-image: linear-gradient(#ffffff, #bee1fe);
      flex-shrink: 0;
      align-self: center;
    }
  }

  .actions {
    display: flex;

    a {
      padding: 0;
      color: var(--colour-ti-highlight);
      font-size: .75rem;
    }

    :deep(.base.link.filled) .icon,
    :deep(.base.link.filled) .icon svg {
      width: 16px !important;
      height: 16px !important;
    }
  }
}

.appointment-call-out {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  justify-content: center;
  align-items: center;

  border-radius: 1rem;
  padding: 1.5rem 1.5rem 3.5rem;
  max-width: 23rem;

  background-image: radial-gradient(circle at bottom right, #336d71, #1b222e 85%);
  color: var(--colour-neutral-lower-light);
  font-family: Inter, sans-serif;
  text-align: center;
  
  .tagline {
    font-size: 2rem;
    font-weight: 300;
    font-family: Metropolis, sans-serif;
  }

  .description {
    font-size: 0.875rem;
    color: var(--colour-neutral-lower);
  }

  :deep(.base.primary.filled) {
    position: relative;
    z-index: 1;
    background-image: linear-gradient(161deg, #a0e1ff -26%, #2b8cdc 45%);
    color: var(--colour-ti-base);
    text-transform: uppercase;
    font-weight: 600;
    font-size: 0.8125rem;

    &::before {
      content: '';
      position: absolute;
      z-index: -1;
      width: calc(100% - 2px);
      height: calc(100% - 2px);
      background-image: linear-gradient(353deg, #1373d9 -36%, #58c9ff);
      border-radius: .5rem;
    }
  }
}
</style>
