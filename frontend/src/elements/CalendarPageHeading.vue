<template>
  <div
    class="mx-auto mb-2 flex select-none items-center gap-4 lg:mx-0 lg:mb-8 lg:gap-8"
  >
    <div
      v-if="nav"
      @click="emit('prev')"
      class="group cursor-pointer select-none"
    >
      <icon-chevron-left
        class="size-10 fill-transparent stroke-gray-400 stroke-1 group-hover:stroke-teal-500"
      />
    </div>
    <h2 v-if="title && !backlink" class="flex flex-col">
      <div class="text-4xl font-light">{{ title }}</div>
      <div class="flex gap-2 text-xl">
        <span class="font-semibold">{{ month }}</span>
        <span>{{ year }}</span>
      </div>
    </h2>
    <h2 v-if="!title && !backlink" class="flex gap-3 text-4xl">
      <span class="font-normal">{{ month }}</span>
      <span class="font-light">{{ year }}</span>
    </h2>
    <h2 v-if="title && backlink" class="flex gap-4 text-4xl font-light">
      <div
        class="flex cursor-pointer gap-3 border-b-2 border-teal-500 text-teal-500"
        @click="emit('back')"
      >
        <span class="font-normal">{{ month }}</span>
        <span>{{ year }}</span>
      </div>
      <icon-chevron-right
        class="size-10 fill-transparent stroke-gray-400 stroke-1"
      />
      <div>{{ title }}</div>
    </h2>
    <div
      v-if="nav"
      @click="emit('next')"
      class="group cursor-pointer select-none"
    >
      <icon-chevron-right
        class="size-10 fill-transparent stroke-gray-400 stroke-1 group-hover:stroke-teal-500"
      />
    </div>
  </div>
</template>

<script setup>
// icons
import { IconChevronLeft, IconChevronRight } from '@tabler/icons-vue';

// component properties
defineProps({
  month: String, // month of active date
  year: String, // year of active date
  title: String, // title of current calendar view (optional)
  nav: Boolean, // show navigation
  backlink: Boolean, // show breadcrumb title with backlink
});

// component emits
const emit = defineEmits(['prev', 'next', 'back']);
</script>
