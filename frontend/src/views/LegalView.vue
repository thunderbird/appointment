<script setup lang="ts">
import {
  computed, onMounted, ref,
} from 'vue';
import { useRoute } from 'vue-router';
/* eslint import/no-unresolved: [2, { ignore: ['\\.html'] }] */
import privacy from '@/assets/legal/en/privacy.html?raw';
import terms from '@/assets/legal/en/terms.html?raw';

const route = useRoute();

const pageContents = ref('');
const isTerms = computed(() => route.name === 'terms');

onMounted(async () => {
  if (isTerms.value) {
    pageContents.value = terms;
  } else {
    pageContents.value = privacy;
  }
});
</script>

<template>
  <div class="page-contents" v-html="pageContents"></div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.page-contents {
  padding: 0 1rem 1rem;

  @media (--md) {
    padding: 0 5rem 2rem;
  }
}

/* Needed for v-html */
:deep {
  h1, h2, h3, h4 {
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
