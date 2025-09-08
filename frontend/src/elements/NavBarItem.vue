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
    :class="{ 'active': !active }"
  >
    <router-link :to="{ name: linkName }">
      {{ label }}
    </router-link>
  </div>
</template>

<style scoped>
  .nav-bar-item-container {
    display: flex;
    align-items: center;
    font-family: metropolis;
    font-size: 0.8125rem;
    font-weight: 600;
    text-transform: uppercase;
    color: #EEEEF0; /* TODO: --colour-ti-base but we don't have light mode for nav bar yet */

    &.active {
      color: #D9D9DE; /* TODO: --colour-ti-secondary but we don't have light mode for nav bar yet */
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