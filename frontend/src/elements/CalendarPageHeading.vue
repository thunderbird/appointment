<template>
  <div class="flex gap-8 items-center">
    <div @click="emit('prev')" class="group cursor-pointer">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 stroke-slate-400 group-hover:stroke-teal-500 stroke-1 fill-transparent" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">
        <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
        <polyline points="15 6 9 12 15 18" />
      </svg>
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
    <div @click="emit('next')" class="group cursor-pointer">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 stroke-slate-400 group-hover:stroke-teal-500 stroke-1 fill-transparent" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">
        <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
        <polyline points="9 6 15 12 9 18" />
      </svg>
    </div>
  </div>
</template>

<script setup>
// component properties
defineProps({
  month:  String, // month of active date
  year:   String, // year of active date
  title:  String, // title of current calendar view (optional)
});

// component emits
const emit = defineEmits(['prev', 'next']);
</script>
