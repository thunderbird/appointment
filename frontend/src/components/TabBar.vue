<template>
  <div class="rounded-2xl bg-gray-200">
    <nav class="flex">
      <ul class="flex justify-between w-full gap-4 p-1">
        <li
          v-for="(item, i) in tabItems"
          :key="item"
          class="flex whitespace-nowrap leading-8 cursor-pointer px-8 transition-all ease-in-out hover:rounded-xl"
          :class="{
            'text-gray-900 bg-white rounded-xl shadow': i == active,
            'text-gray-500 hover:bg-gray-100': i != active,
          }"
          @click="activate(item)"
        >
          {{ t('label.' + item) }}
        </li>
      </ul>
    </nav>
  </div>
</template>

<script setup>
import { useI18n } from "vue-i18n";
const { t } = useI18n();

// component properties
defineProps({
  tabItems: Array, // list of tab names that are also lang keys (label.<key>), used as tab items
  active: Number   // index of active tab
});

// component emits
const emit = defineEmits(['update']);

// handle click events
const activate = (item) => {
  emit('update', item);
}
</script>
