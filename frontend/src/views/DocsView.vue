<script setup lang="ts">
import {
  onMounted, ref,
} from 'vue';
/* eslint import/no-unresolved: [2, { ignore: ['\\.html'] }] */
import usingZoom from '@/assets/docs/en/using-zoom.html?raw';

const pageContents = ref('');

onMounted(async () => {
  pageContents.value = usingZoom;
});
</script>

<template>
  <div class="page-contents" v-html="pageContents"></div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.page-contents {
  padding: 0 1rem;

  @media (--md) {
    padding: 0 5rem;
  }

  @media (--lg) {
    display: flex;
    flex-direction: column;
    position: relative;
    max-width: 70%;
    margin-bottom: 10%;
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
    padding-top: .5rem;
    padding-bottom: .5rem;
    line-height: 1.625;
  }

  a {
    text-decoration-line: underline;
  }

  .toc {
    @media (--lg) {
      display: flex;
      flex-direction: column;
      right: 5%;
      position: fixed;
      margin-top: 3%;
    }
  }

  .toc ul:first-child {
    font-weight: 600;
    margin-left: 0.5rem;
  }

  .toc ul ul {
    font-weight: 400;
    margin-top: 0.5rem;
    margin-left: 2rem;
    list-style: decimal;
  }

}
</style>
