<template>
  <base-button type="primary">
    <template v-for="(_, name) in $slots" v-slot:[name]="slotData">
      <slot :name="name" v-bind="slotData" />
    </template>
  </base-button>
</template>
<script setup>
import BaseButton from '@/tbpro/elements/BaseButton.vue';
</script>
