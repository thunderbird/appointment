<script setup lang="ts">
import ExternalRedirect from '@/components/ExternalRedirect.vue';

const redirectUrl = import.meta.env?.VITE_SUPPORT_URL;

</script>
<template>
  <external-redirect :redirect-url="redirectUrl"/>
</template>
