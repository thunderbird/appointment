<script setup lang="ts">
interface Props {
  title: string;
}
defineProps<Props>();
</script>

<template>
  <div class="mb-20 flex w-full flex-col shadow-[0_-5px_5px_-5px_rgb(0_0_0/0.3)] md:w-1/3
">
    <div class="m-4 flex h-16 gap-4">
      <!--<img class="w-[64px] h-[64px]" src="@/assets/svg/icon-wand.svg"/>-->
      <h3 class="my-auto text-2xl text-teal-600 dark:text-teal-400">{{ title }}</h3>
    </div>
    <div class="m-4 mb-8">
      <p class="text-lg leading-loose"><slot></slot></p>
    </div>
  </div>
</template>
