<script setup lang="ts">
import { onMounted } from 'vue';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';

// component properties
interface Props {
  redirectUrl: string
}

const props = withDefaults(defineProps<Props>(), {
  redirectUrl: '/',
});

const redirect = async () => {
  window.location.replace(props.redirectUrl);
};

onMounted(() => {
  redirect();
});
</script>
<template>
  <div class="full-page">
    <h2>
      <i18n-t keypath="text.redirectedNotice">
        <template v-slot:url>
          <a class="underline underline-offset-2"
             :href="redirectUrl">
            {{ redirectUrl }}
          </a>
        </template>
      </i18n-t>
    </h2>
    <loading-spinner/>
  </div>
</template>
<style scoped>
@import '@/assets/styles/mixins.pcss';

.full-page {
  @mixin faded-background var(--colour-neutral-border);

  position: fixed;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  justify-content: center;
  align-items: center;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 50;
}
</style>
