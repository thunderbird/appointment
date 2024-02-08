<template>
  <div class="relative">
    <textarea
      v-model="details"
      :placeholder="placeholder"
      class="rounded-md w-full text-sm h-40 place-holder"
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

<script setup>
import { computed } from 'vue';

// component properties
const props = defineProps({
  placeholder: String, // Textarea placeholder text
  maxlength: Number, // text to copy to clipboard
});

// component models
const details = defineModel();

// handle textarea char limit
const charCount = computed(() => details.value.length);
const limitIsClose = computed(() => charCount.value >= props.maxlength * 0.92)
const limitIsReached = computed(() => charCount.value >= props.maxlength)

</script>
