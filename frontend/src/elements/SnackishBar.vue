<script setup lang="ts">
import { IconInfoCircle } from '@tabler/icons-vue';

// component properties
interface Props {
  showIcon?: boolean;
};
withDefaults(defineProps<Props>(), {
  showIcon: false,
})
</script>

<template>
  <div class="h-28 w-full rounded-xl bg-neutral-600 text-white dark:bg-gray-800 dark:text-gray-100">
    <div class="m-auto flex h-full w-8/12 flex-row items-center justify-center gap-2 text-wrap text-center text-xs leading-4 tracking-wider">
      <div class="flex flex-row items-center justify-center gap-2">
        <icon-info-circle v-if="showIcon" class="min-w-4" aria-hidden="true"/>
        <slot></slot>
      </div>
    </div>
  </div>
</template>
