<template>
  <div class="flex flex-col mb-20 w-full md:w-1/3 shadow-[0_-5px_5px_-5px_#3B455F19]">
    <div class="h-16 flex gap-4 m-4">
      <!--<img class="w-[64px] h-[64px]" src="@/assets/svg/icon-wand.svg"/>-->
      <h3 class="text-2xl text-teal-600 my-auto">{{ title }}</h3>
    </div>
    <div class="m-4 mb-8">
      <p class="text-lg leading-loose"><slot></slot></p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
});
</script>
