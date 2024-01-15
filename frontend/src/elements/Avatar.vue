<template>
<div
  class="w-12 h-12 mr-4 self-center flex-center rounded-full text-lg bg-white font-normal text-white"
  :class="{'!bg-teal-500': user.data.avatarUrl === null}"
>
  <span v-if="user.data.avatarUrl === null">
    {{ initials(user.data.name) }}
  </span>
  <span v-else>
    <img class="rounded-full w-[48px] h-[48px]" :alt="initials(user.data.name)" :src="user.data.avatarUrl"/>
  </span>
</div>
</template>

<script setup>
import { initials } from '@/utils';
import { useUserStore } from '@/stores/user-store';
const user = useUserStore();
</script>
