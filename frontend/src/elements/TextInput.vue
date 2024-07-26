<script setup lang="ts">
import { computed } from 'vue';

// component properties
const props = defineProps({
  placeholder: String, // Textarea placeholder text
  maxlength: Number, // text to copy to clipboard
});

// component models
const details = defineModel<string>();

// handle textarea char limit
const charCount = computed(() => details.value.length);
const limitIsClose = computed(() => charCount.value >= props.maxlength * 0.92);
const limitIsReached = computed(() => charCount.value >= props.maxlength);

</script>

<template>
  <div class="relative">
    <textarea
      v-model="details"
      :placeholder="placeholder"
      class="place-holder h-40 w-full rounded-md text-sm"
      :maxlength="maxlength"
      required
    ></textarea>
    <div
      class="absolute bottom-3 right-3 text-xs"
      :class="{
        'text-orange-500': limitIsClose,
        '!text-rose-600': limitIsReached,
      }"
    >
      {{ charCount }}/{{ maxlength }}
    </div>
  </div>
</template>
