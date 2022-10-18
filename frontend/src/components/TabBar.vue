<template>
  <div class="rounded-2xl bg-gray-200">
    <nav class="flex gap-8 items-stretch">
      <ul class="flex justify-end gap-4 p-1">
        <li
          v-for="(item, i) in tabItems"
          :key="item"
          class="flex text-xl leading-8 border-b-4 border-b-transparent cursor-pointer px-8 transition-all ease-in-out"
          :class="{
            'text-gray-900 bg-white rounded-xl shadow': i == active,
            'text-gray-500': i != active,
          }"
          @click="activate(i)"
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
const activate = (n) => {
  emit('update', n);
}
</script>
