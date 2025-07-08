<script setup lang="ts">
import { initials } from '@/utils';
import { useUserStore } from '@/stores/user-store';

const user = useUserStore();
</script>

<template>
<div
  class="flex-center size-8 self-center rounded-full bg-white text-sm font-semibold text-white"
  :class="{'!bg-teal-500': user.data.avatarUrl === null}"
  data-testid="user-menu-avatar"
>
  <span v-if="user.data.avatarUrl === null">
    {{ initials(user.data.name) }}
  </span>
  <span v-else>
    <img class="size-[48px] rounded-full" :alt="initials(user.data.name)" :src="user.data.avatarUrl"/>
  </span>
</div>
</template>
