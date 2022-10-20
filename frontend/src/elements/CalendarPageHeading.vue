<template>
  <div class="flex gap-8 items-center select-none">
    <div @click="emit('prev')" class="group cursor-pointer select-none">
      <icon-chevron-left class="h-10 w-10 stroke-slate-400 group-hover:stroke-teal-500 stroke-1 fill-transparent" />
    </div>
    <h2 v-if="title" class="flex flex-col">
      <div class="text-4xl font-light">{{ title }}</div>
      <div class="flex gap-2">
        <span class="text-xl font-semibold">{{ month }}</span>
        <span class="text-xl">{{ year }}</span>
      </div>
    </h2>
    <h2 v-else class="flex gap-3">
      <span class="text-4xl font-normal">{{ month }}</span>
      <span class="text-4xl font-light">{{ year }}</span>
    </h2>
    <div @click="emit('next')" class="group cursor-pointer select-none">
      <icon-chevron-right class="h-10 w-10 stroke-slate-400 group-hover:stroke-teal-500 stroke-1 fill-transparent" />
    </div>
  </div>
</template>

<script setup>
import IconChevronLeft from './icons/IconChevronLeft.vue';
import IconChevronRight from './icons/IconChevronRight.vue';

// component properties
defineProps({
  month:  String, // month of active date
  year:   String, // year of active date
  title:  String, // title of current calendar view (optional)
});

// component emits
const emit = defineEmits(['prev', 'next']);
</script>
