<script setup lang="ts">
import { computed, inject, ref } from 'vue';
import { refreshKey } from '@/keys';
import { PhArrowClockwise } from '@phosphor-icons/vue';
import { storeToRefs } from 'pinia';
import { formatTimeAgoIntl, useNow } from '@vueuse/core';
import { useI18n } from 'vue-i18n';
import { Dayjs } from 'dayjs';
import { useCalendarStore } from '@/stores/calendar-store';
import { useScheduleStore } from '@/stores/schedule-store';
import { useUserStore } from '@/stores/user-store';

const loading = defineModel<boolean>('loading', { required: true });

const props = defineProps<{
  activeDate: Dayjs,
}>();

const refresh = inject(refreshKey);
const { t } = useI18n();

const calendarStore = useCalendarStore();
const userStore = useUserStore();
const scheduleStore = useScheduleStore();

const { firstSchedule } = storeToRefs(scheduleStore);

const lastRefreshedTime = ref(new Date());

const { now } = useNow({ interval: 30000, controls: true });
const timeAgo = computed(() =>
  formatTimeAgoIntl(lastRefreshedTime.value, { locale: userStore?.data?.settings?.language }, now.value)
);

const scheduleCalendar = computed(() => {
  return calendarStore.calendarById(firstSchedule.value?.calendar_id)
})

async function onSyncCalendarButtonClicked() {
  loading.value = true;

  await refresh();
  await calendarStore.getRemoteEvents(props.activeDate, true);

  const currentTime = new Date();
  lastRefreshedTime.value = currentTime;
  now.value = currentTime;

  loading.value = false;
}
</script>

<template>
  <div class="user-info-container">
    <template v-if="scheduleCalendar?.connected">
      <div>
        <p class="user-email">{{ scheduleCalendar?.user }}</p>
        <p class="user-updated-at">{{ t('label.updated') }} {{ timeAgo }}</p>
      </div>

      <button @click="onSyncCalendarButtonClicked" :disabled="loading" :class="{ 'loading': loading }">
        <ph-arrow-clockwise size="24" />
      </button>
    </template>
    <template v-else>
      <p>{{ t('label.disconnected') }}</p>
    </template>
  </div>
</template>

<style scoped>
.user-info-container {
  display: flex;
  align-items: center;
  justify-content: end;
  text-align: right;
  gap: 0.5rem;
  width: 100%;
  padding-inline-end: 0.3rem;

  button {
    color: var(--colour-ti-secondary);
  }

  button.loading {
    color: var(--colour-ti-muted);
    cursor: not-allowed;
  }

  .user-email {
    font-size: 0.75rem;
    color: var(--colour-ti-base);
  }

  .user-updated-at {
    font-size: 0.6875rem;
    color: var(--colour-ti-secondary);
  }
}

@media (prefers-reduced-motion: no-preference) {
  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }

  button.loading {
    animation: spin 1s linear infinite;
  }
}
</style>