<template>
  <div v-html="pageContents">
  </div>
</template>

<script setup>
import {
  inject, computed, onMounted, ref,
} from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

// component constants
const call = inject('call');

const pageContents = ref('');
const isTerms = computed(() => route.name === 'terms');

onMounted(async () => {
  const url = isTerms.value ? 'terms' : 'privacy';
  console.log(route.name);

  const response = await (await call(url)).json();

  if (response?.data) {
    pageContents.value = response?.data?.value;
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
