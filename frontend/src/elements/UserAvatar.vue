<template>
<div
  class="flex-center mr-4 size-12 self-center rounded-full bg-white text-lg font-normal text-white"
  :class="{'!bg-teal-500': user.data.avatarUrl === null}"
>
  <span v-if="user.data.avatarUrl === null">
    {{ initials(user.data.name) }}
  </span>
  <span v-else>
    <img class="size-[48px] rounded-full" :alt="initials(user.data.name)" :src="user.data.avatarUrl"/>
  </span>
</div>
</template>

<script setup>
import { initials } from '@/utils';
import { useUserStore } from '@/stores/user-store';

const user = useUserStore();
</script>
