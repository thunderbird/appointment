<template>
  <div class="rounded-2xl bg-gray-200">
    <nav class="flex">
      <ul class="flex justify-between w-full gap-4 p-1">
        <li
          v-for="(item, key) in tabItems"
          :key="item"
          class="flex whitespace-nowrap leading-8 cursor-pointer px-8 transition-all ease-in-out hover:rounded-xl"
          :class="{
            'text-gray-900 bg-white rounded-xl shadow': item == active,
            'text-gray-500 hover:bg-gray-100': item != active,
          }"
          @click="activate(key)"
        >
          {{ t('label.' + key) }}
        </li>
      </ul>
    </nav>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

// component properties
defineProps({
  tabItems: Object, // list of tab items. Keys are used as lang keys (label.<key>), values as index
  active: Number    // value of active tab
});

// component emits
const emit = defineEmits(['update']);

// handle click events
const activate = (key) => {
  emit('update', key);
}
</script>
