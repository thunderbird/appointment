<script setup lang="ts">
import { computed, nextTick, watch } from 'vue';
import { useRoute } from 'vue-router';
/* eslint import/no-unresolved: [2, { ignore: ['\\.html'] }] */
import privacy from '@/assets/legal/en/privacy.html?raw';
import terms from '@/assets/legal/en/terms.html?raw';

const route = useRoute();

const isTerms = computed(() => route.name === 'terms');
const pageContents = computed(() => (isTerms.value ? terms : privacy));

// Since we are using the same component for both privacy and terms routes,
// we need to use a watch here to scroll to the top when the route changes
// otherwise the scroll would remain at the bottom
watch(
  () => route.fullPath,
  async () => {
    await nextTick();
    window.scrollTo({ top: 0, left: 0, behavior: 'auto' });
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0;
  },
  { immediate: true }
);
</script>

<template>
  <div class="page-contents" v-html="pageContents"></div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.page-contents {
  padding: 0 1rem 1rem;

  @media (--md) {
    padding: 0 3.75rem 2rem;
  }
}

/* Needed for v-html */
:deep {
  h1,
  h2,
  h3,
  h4 {
    color: var(--colour-ti-highlight);
  }

  h1 {
    padding-top: 2rem;
    padding-bottom: 2rem;
    font-size: 1.875rem;
    line-height: 2.25rem;
  }

  h2 {
    padding-top: 2rem;
    padding-bottom: 2rem;
    font-size: 1.5rem;
    line-height: 2rem;
  }

  h3 {
    padding-top: 1rem;
    padding-bottom: 1rem;
    font-size: 1.25rem;
    line-height: 1.75rem;
  }

  h4 {
    padding-top: 1rem;
    padding-bottom: 1rem;
    font-size: 1.125rem;
    line-height: 1.75rem;
  }

  p {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
    line-height: 1.625;
  }

  p:first-of-type {
    font-weight: 600;
  }

  a {
    text-decoration-line: underline;
  }
}
</style>
