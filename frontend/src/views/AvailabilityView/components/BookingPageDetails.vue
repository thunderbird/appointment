<script setup lang="ts">
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
</script>

<template>
  <h2>Booking Page Details</h2>
  <div class="mb-1 px-4">
    <label for="scheduleName" class="flex-column flex">
      <input
        id="scheduleName"
        type="text"
        :placeholder="t('placeholder.mySchedule')"
        class="schedule-name place-holder w-full rounded-none border-0 border-b bg-transparent p-1 dark:bg-transparent"
        required
      />
      <!-- <div v-if="!scheduleInput.name" class="content-center text-red-500">*</div> -->
    </label>
  </div>
</template>

<style scoped>
h2 {
  font-size: 1.5rem;
}
</style>