<script setup lang="ts">
import { computed, inject, onMounted, ref } from 'vue';
import { callKey, refreshKey } from '@/keys';
import { PhArrowClockwise } from '@phosphor-icons/vue';
import { storeToRefs } from 'pinia';
import { useTimeAgoIntl } from '@vueuse/core';
import { useI18n } from 'vue-i18n';
import { useCalendarStore } from '@/stores/calendar-store';
import { createScheduleStore } from '@/stores/schedule-store';
import { useUserStore } from '@/stores/user-store';

const refresh = inject(refreshKey);
const call = inject(callKey);
const { t } = useI18n();

const loading = ref(false);
const lastRefreshedTime = ref(Date.now());

const calendarStore = useCalendarStore();
const userStore = useUserStore();
const scheduleStore = createScheduleStore(call);
const { firstSchedule } = storeToRefs(scheduleStore);

const scheduleCalendar = computed(() => {
  return calendarStore.calendarById(firstSchedule.value?.calendar_id)
})

const timeAgo = userStore?.data?.settings?.language && useTimeAgoIntl(lastRefreshedTime, { locale: userStore.data.settings.language });

async function onSyncCalendarButtonClicked() {
  loading.value = true;

  await calendarStore.syncCalendars();
  await refreshData();
  lastRefreshedTime.value = Date.now();

  loading.value = false;
}

async function refreshData() {
  calendarStore.$reset();
  await refresh();
};

onMounted(async () => {
  await scheduleStore.fetch();
})
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