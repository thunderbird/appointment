<template>
  <div class="px-4 md:px-20" v-html="pageContents"></div>
</template>

<script setup>
import {
  computed, onMounted, ref,
} from 'vue';
import { useRoute } from 'vue-router';
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
<style scoped>
/* Needed for v-html */
:deep {
  h1  {
    @apply py-8 text-3xl text-teal-600 dark:text-teal-400;
  }
  h2 {
    @apply py-8 text-2xl text-teal-600 dark:text-teal-400;
  }
  h3 {
    @apply py-4 text-lg text-teal-600 dark:text-teal-400;
  }
  h4 {
    @apply py-4 text-lg text-teal-600 dark:text-teal-400;
  }
  p {
    @apply py-2 leading-relaxed;
  }
  p:first-of-type {
    @apply font-semibold;
  }
}
</style>
