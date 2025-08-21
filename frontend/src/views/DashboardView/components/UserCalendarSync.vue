<script setup lang="ts">
import { computed, inject, onMounted, ref } from 'vue';
import { callKey, refreshKey } from '@/keys';
import { IconReload } from '@tabler/icons-vue';
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

const timeAgo = useTimeAgoIntl(lastRefreshedTime, { locale: userStore.data.settings.language });

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
        <p>{{ t('label.connected') }} - <strong>{{ scheduleCalendar?.user }}</strong></p>
        <p>{{ t('label.updated') }} {{ timeAgo }}</p>
      </div>

      <button @click="onSyncCalendarButtonClicked" :disabled="loading" :class="{ 'loading': loading }">
        <icon-reload size="20"/>
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
  font-size: 0.875rem;
  gap: 1rem;
  width: 100%;

  button.loading {
    color: var(--colour-ti-muted);
    cursor: not-allowed;
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