<script setup lang="ts">
import type { Dayjs } from 'dayjs';
import { computed, inject } from 'vue';
import { useI18n } from 'vue-i18n';
import { dayjsKey } from '@/keys';
import { BaseBadge, BaseBadgeTypes } from '@thunderbirdops/services-ui';

const props = defineProps<{
  name: string;
  email: string;
  requestDate: string;
  meetingDate: string | Dayjs;
  needsConfirmation: boolean;
}>();

const dj = inject(dayjsKey);
const { t } = useI18n();

const formattedRequestDate = computed(() => dj(props.requestDate).format('L, LT'));
const formattedMeetingDate = computed(() => dj(props.meetingDate).format('L, LT'));
</script>

<template>
  <div class="appointment-item">
    <div>
      <strong>{{ name }}</strong>
      <p>{{ email }}</p>
    </div>

    <div>
      <p>{{ t('label.requestDate') }}</p>
      <strong>{{ formattedRequestDate }}</strong>
    </div>

    <div>
      <p>{{ t('label.meetingDate') }}</p>
      <strong>{{ formattedMeetingDate }}</strong>
    </div>

    <div>
      <base-badge v-if="needsConfirmation" :type="BaseBadgeTypes.NotSet">
        {{ t('label.needsConfirmation') }}
      </base-badge>
    </div>
  </div>
</template>

<style scoped>
.appointment-item {
  display: grid;
  grid-template-columns: 300px 1fr 1fr 1fr;
  align-items: center;
  background-color: var(--colour-neutral-lower);
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;

  strong {
    font-weight: 600;
    font-size: 1rem;
  }
}
</style>
