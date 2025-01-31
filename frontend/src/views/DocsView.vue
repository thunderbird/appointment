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
  <div class="page-contents px-4 md:px-20" v-html="pageContents"></div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.page-contents {

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
  h1 {
    @apply py-8 text-3xl text-teal-600 dark:text-teal-400;
  }

  h2 {
    @apply py-8 text-2xl text-teal-600 dark:text-teal-400;
  }

  h3 {
    @apply py-4 text-xl text-teal-600 dark:text-teal-400;
  }

  h4 {
    @apply py-4 text-lg text-teal-600 dark:text-teal-400;
  }

  p {
    @apply py-2 leading-relaxed;
  }

  a {
    @apply underline;
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
