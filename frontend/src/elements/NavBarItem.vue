<script setup lang="ts">
// component properties
interface Props {
  active: boolean; // indicator for currently active item
  label: string; // item text label
  linkName: string; // name of the route link target
}
defineProps<Props>();
</script>

<template>
  <div
    class="nav-bar-item-container"
    :class="{ 'active': active }"
  >
    <router-link :to="{ name: linkName }">
      {{ label }}
    </router-link>
  </div>
</template>

<style scoped>
  .nav-bar-item-container {
    font-family: metropolis;
    font-size: 0.8125rem;
    font-weight: 600;
    text-transform: uppercase;
    color: var(--colour-ti-base-dark);
    height: 2.25rem;
    border-radius: 8px;

    &.active {
      background-color: var(--colour-neutral-lower-dark);
    }

    a {
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      min-width: 120px;
      height: 100%;
    }
  }
</style>