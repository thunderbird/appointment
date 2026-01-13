<script setup lang="ts">
import { computed, inject } from 'vue';
import { timeFormat, toTitleCase } from '@/utils';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user-store';

import PrimaryButton from '@/elements/PrimaryButton.vue';
import { dayjsKey } from '@/keys';
import { Appointment, Attendee, Slot } from '@/models';

const { t } = useI18n();
const router = useRouter();

const dj = inject(dayjsKey);
const user = useUserStore();

// component properties
interface Props {
  selectedEvent: Appointment & Slot,
  attendee: Attendee,
  requested: boolean, // True if we are requesting a booking, false if already confirmed
}
const props = defineProps<Props>();

const heading = computed(() => toTitleCase(props.requested
  ? t('info.bookingSuccessfullyRequested')
  : t('info.bookingSuccessfullyConfirmed')
));
</script>

<template>
  <div>
    <div class="heading">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M10.452 4.934a1.482 1.482 0 0 0-2.437.541L3.094 19.011A1.484 1.484 0 0 0 4.478 21c.174-.001.348-.033.511-.094l13.535-4.922a1.48 1.48 0 0 0 .542-2.437l-8.614-8.613zm-.78 12.676L6.39 14.329l1.234-3.395 5.442 5.442-3.395 1.234zm-5.157 1.875 1.313-3.6 2.292 2.291-3.605 1.309zm10.11-3.675L8.19 9.375 9.41 6.012l8.571 8.572-3.355 1.226zM15 6.75a3.543 3.543 0 0 1 .36-1.46c.497-.993 1.434-1.54 2.64-1.54.628 0 1.031-.215 1.28-.676.13-.258.206-.54.22-.83a.75.75 0 1 1 1.5.006c0 1.206-.799 3-3 3-.628 0-1.031.215-1.28.676-.13.258-.205.54-.22.83A.751.751 0 0 1 15 6.75zm-2.25-3V1.5a.75.75 0 1 1 1.5 0v2.25a.75.75 0 1 1-1.5 0zm9.53 7.72a.752.752 0 0 1-.53 1.28.75.75 0 0 1-.53-.22l-1.5-1.5a.75.75 0 0 1 1.06-1.062l1.5 1.501zm.457-4.008-2.25.75a.75.75 0 0 1-.474-1.424l2.25-.75a.75.75 0 1 1 .474 1.424z" />
      </svg>
      {{ heading }}
    </div>
    {{ dj(selectedEvent.start).format('dddd') }}
    {{ dj(selectedEvent.start).format('LL') }}
    <span>{{ dj(selectedEvent.start).format(timeFormat()) }}</span>
    <span>{{ dj.tz.guess() }}</span>
    <primary-button
      v-if="!user.authenticated"
      class="btn-start mt-12 p-7"
      :label="t('label.startUsingTba')"
      @click="router.push({ name: 'home' })"
    />
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.heading {
  display: flex;
  align-items: center;
  gap: 0.5rem;

  color: var(--colour-ti-highlight);
  font-size: 1.5rem;
  font-family: Inter, sans-serif;

  svg {
    fill: var(--colour-ti-highlight);
  }
}
</style>
