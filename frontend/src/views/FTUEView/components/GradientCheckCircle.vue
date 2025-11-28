<script setup lang="ts">
import { PhCheckCircle } from '@phosphor-icons/vue';
</script>

<template>
  <div>
    <!--
      Defining the gradient here allows us to use it in the icon fill.
      We use a fixed ID, so if multiple instances are present, they all share the same gradient definition.
    -->
    <svg width="0" height="0" style="position: absolute; pointer-events: none; opacity: 0;">
      <defs>
        <linearGradient id="ftue-check-gradient" gradientTransform="rotate(76 .5 .5)">
          <stop offset="0%" stop-color="#66a47a" />
          <stop offset="90%" stop-color="#1d783b" />
          <stop offset="100%" stop-color="#1d783b" />
        </linearGradient>
      </defs>
    </svg>
    <ph-check-circle class="check-circle-icon" weight="fill" />
  </div>
</template>

<style scoped>
.check-circle-icon {
  width: 2.25rem;
  height: 2.25rem;
  fill: url(#ftue-check-gradient);
}
</style>

