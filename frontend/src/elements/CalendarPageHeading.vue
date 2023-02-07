<template>
  <div class="flex gap-8 items-center select-none">
    <div v-if="nav" @click="emit('prev')" class="group cursor-pointer select-none">
      <chevron-left-icon class="h-10 w-10 stroke-slate-400 group-hover:stroke-teal-500 stroke-1 fill-transparent" />
    </div>
    <h2 v-if="(title && !backlink)" class="flex flex-col">
      <div class="text-4xl font-light">{{ title }}</div>
      <div class="flex gap-2 text-xl">
        <span class="font-semibold">{{ month }}</span>
        <span>{{ year }}</span>
      </div>
    </h2>
    <h2 v-if="(!title && !backlink)" class="flex gap-3 text-4xl">
      <span class="font-normal">{{ month }}</span>
      <span class="font-light">{{ year }}</span>
    </h2>
    <h2 v-if="(title && backlink)" class="flex gap-4 text-4xl font-light">
      <div class="flex gap-3 text-teal-500 cursor-pointer border-b-2 border-teal-500" @click="emit('back')">
        <span class="font-normal">{{ month }}</span>
        <span>{{ year }}</span>
      </div>
      <chevron-right-icon class="h-10 w-10 stroke-slate-400 stroke-1 fill-transparent" />
      <div>{{ title }}</div>
    </h2>
    <div v-if="nav" @click="emit('next')" class="group cursor-pointer select-none">
      <chevron-right-icon class="h-10 w-10 stroke-slate-400 group-hover:stroke-teal-500 stroke-1 fill-transparent" />
    </div>
  </div>
</template>

<script setup>
// icons
import {
  ChevronLeftIcon,
  ChevronRightIcon,
} from "vue-tabler-icons";

// component properties
defineProps({
  month:    String,  // month of active date
  year:     String,  // year of active date
  title:    String,  // title of current calendar view (optional)
  nav:      Boolean, // show navigation
  backlink: Boolean, // show breadcrumb title with backlink
});

// component emits
const emit = defineEmits(['prev', 'next', 'back']);
</script>
