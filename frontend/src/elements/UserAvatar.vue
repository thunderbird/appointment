<script setup lang="ts">
import { initials } from '@/utils';
import { useUserStore } from '@/stores/user-store';

const user = useUserStore();
</script>

<template>
<div
  class="user-avatar"
  :class="{'user-avatar--fallback': user.data.avatarUrl === null}"
  data-testid="user-menu-avatar"
>
  <span v-if="user.data.avatarUrl === null">
    {{ initials(user.data.name) }}
  </span>
  <span v-else>
    <img class="user-avatar__image" :alt="initials(user.data.name)" :src="user.data.avatarUrl"/>
  </span>
</div>
</template>

<style scoped>
.user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  align-self: center;
  border-radius: 50%;
  background-color: var(--colour-neutral-base);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--colour-neutral-base);
}

.user-avatar--fallback {
  background-color: var(--colour-accent-teal);
}

.user-avatar__image {
  border-radius: 50%;
}
</style>