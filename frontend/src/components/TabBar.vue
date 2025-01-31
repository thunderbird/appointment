<script setup lang="ts">
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

// component properties
interface Props {
  tabItems: object, // list of tab items. Keys are used as lang keys (label.<key>), values as index
  active: number, // value of active tab
  disabled?: boolean, // flag for making toggle non changable
}
defineProps<Props>();

// component emits
const emit = defineEmits(['update']);

// handle click events
const activate = (key: string) => {
  emit('update', key);
};
</script>

<template>
  <div class="rounded-2xl bg-gray-200 dark:bg-gray-600">
    <nav class="flex">
      <ul class="flex w-full justify-between p-1 md:gap-4">
        <li
          v-for="(item, key) in tabItems"
          :key="item"
          class="flex whitespace-nowrap px-8 leading-8 transition-all ease-in-out hover:rounded-xl"
          :class="{
            'cursor-pointer': !disabled,
            'rounded-xl shadow dark:bg-gray-500': item == active,
            'bg-white text-gray-900 dark:text-white': item == active && !disabled,
            'bg-gray-100 text-gray-600 dark:text-gray-300': item == active && disabled,
            'text-gray-500 dark:text-gray-300': item != active,
            'hover:bg-gray-100 dark:hover:bg-gray-700': item != active && !disabled,
          }"
          @click="!disabled ? activate(key) : null"
          :data-testid="'booking-' + key + '-btn'"
        >
          {{ t('label.' + key) }}
        </li>
      </ul>
    </nav>
  </div>
</template>
