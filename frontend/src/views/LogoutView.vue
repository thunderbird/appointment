<script setup lang="ts">
import { inject, onMounted } from 'vue';
import { callKey } from '@/keys';
import { useUserStore } from '@/stores/user-store';

import { useRouter } from 'vue-router';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';

// component constants
const user = useUserStore();
const router = useRouter();

const call = inject(callKey);

// do log out
const logout = async () => {
  await user.logout(call);
  await router.push('/');
};

onMounted(() => {
  logout();
});
</script>
<template>
  <div class="full-page">
    <loading-spinner/>
  </div>
</template>
<style scoped>
  @import '@/assets/styles/mixins.pcss';
  .full-page {
    @mixin faded-background var(--colour-neutral-border);

    position: fixed;
    display: flex;
    justify-content: center;
    align-items: center;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 50;
  }
</style>
