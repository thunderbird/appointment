<script setup lang="ts">
import { inject } from 'vue';
import { timeFormat, toTitleCase } from '@/utils';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user-store';

import { LinkButton, PrimaryButton } from '@thunderbirdops/services-ui';
import { apiUrlKey, dayjsKey } from '@/keys';
import { Appointment, Attendee, Slot } from '@/models';
import { PhArrowRight } from '@phosphor-icons/vue';

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
  ? toTitleCase(t('info.bookingSuccessfullyRequested'))
  : toTitleCase(t('info.bookingSuccessfullyConfirmed'));

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
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M10.452 4.934a1.482 1.482 0 0 0-2.437.541L3.094 19.011A1.484 1.484 0 0 0 4.478 21c.174-.001.348-.033.511-.094l13.535-4.922a1.48 1.48 0 0 0 .542-2.437l-8.614-8.613zm-.78 12.676L6.39 14.329l1.234-3.395 5.442 5.442-3.395 1.234zm-5.157 1.875 1.313-3.6 2.292 2.291-3.605 1.309zm10.11-3.675L8.19 9.375 9.41 6.012l8.571 8.572-3.355 1.226zM15 6.75a3.543 3.543 0 0 1 .36-1.46c.497-.993 1.434-1.54 2.64-1.54.628 0 1.031-.215 1.28-.676.13-.258.206-.54.22-.83a.75.75 0 1 1 1.5.006c0 1.206-.799 3-3 3-.628 0-1.031.215-1.28.676-.13.258-.205.54-.22.83A.751.751 0 0 1 15 6.75zm-2.25-3V1.5a.75.75 0 1 1 1.5 0v2.25a.75.75 0 1 1-1.5 0zm9.53 7.72a.752.752 0 0 1-.53 1.28.75.75 0 0 1-.53-.22l-1.5-1.5a.75.75 0 0 1 1.06-1.062l1.5 1.501zm.457-4.008-2.25.75a.75.75 0 0 1-.474-1.424l2.25-.75a.75.75 0 1 1 .474 1.424z" />
        </svg>
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
            <svg viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
              <path d="M14 9V13C14 13.1326 13.9473 13.2598 13.8536 13.3536C13.7598 13.4473 13.6326 13.5 13.5 13.5H2.5C2.36739 13.5 2.24021 13.4473 2.14645 13.3536C2.05268 13.2598 2 13.1326 2 13V9C2 8.86739 2.05268 8.74021 2.14645 8.64645C2.24021 8.55268 2.36739 8.5 2.5 8.5C2.63261 8.5 2.75979 8.55268 2.85355 8.64645C2.94732 8.74021 3 8.86739 3 9V12.5H13V9C13 8.86739 13.0527 8.74021 13.1464 8.64645C13.2402 8.55268 13.3674 8.5 13.5 8.5C13.6326 8.5 13.7598 8.55268 13.8536 8.64645C13.9473 8.74021 14 8.86739 14 9ZM7.64625 9.35375C7.69269 9.40024 7.74783 9.43712 7.80853 9.46228C7.86923 9.48744 7.93429 9.50039 8 9.50039C8.06571 9.50039 8.13077 9.48744 8.19147 9.46228C8.25217 9.43712 8.30731 9.40024 8.35375 9.35375L10.8538 6.85375C10.9002 6.8073 10.9371 6.75214 10.9622 6.69145C10.9873 6.63075 11.0003 6.5657 11.0003 6.5C11.0003 6.4343 10.9873 6.36925 10.9622 6.30855C10.9371 6.24786 10.9002 6.1927 10.8538 6.14625C10.8073 6.09979 10.7521 6.06294 10.6914 6.0378C10.6308 6.01266 10.5657 5.99972 10.5 5.99972C10.4343 5.99972 10.3692 6.01266 10.3086 6.0378C10.2479 6.06294 10.1927 6.09979 10.1462 6.14625L8.5 7.79313V2C8.5 1.86739 8.44732 1.74021 8.35355 1.64645C8.25979 1.55268 8.13261 1.5 8 1.5C7.86739 1.5 7.74021 1.55268 7.64645 1.64645C7.55268 1.74021 7.5 1.86739 7.5 2V7.79313L5.85375 6.14625C5.75993 6.05243 5.63268 5.99972 5.5 5.99972C5.36732 5.99972 5.24007 6.05243 5.14625 6.14625C5.05243 6.24007 4.99972 6.36732 4.99972 6.5C4.99972 6.63268 5.05243 6.75993 5.14625 6.85375L7.64625 9.35375Z" />
            </svg>
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
          <ph-arrow-right />
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

  background-image: radial-gradient(circle at 100% 100%, #336d71, #1b222e);
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
}
</style>
