<script setup lang="ts">
import BaseButton from '@/tbpro/elements/BaseButton.vue';
</script>

<template>
  <base-button type="primary">
    <template v-for="(_, name) in $slots" v-slot:[name]="slotData">
      <slot :name="name" v-bind="slotData" />
    </template>
  </base-button>
</template>
