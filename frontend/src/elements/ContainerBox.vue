<template>
  <div class="container-box">
    <slot></slot>
  </div>
</template>

<style scoped>
.container-box {
  position: relative;
  text-wrap: wrap;
  border-radius: 0.5rem;
  background-color: var(--colour-neutral-base);
  font-family: 'Inter', sans-serif;
  color: var(--colour-ti-base);
  padding: .75rem .75rem;
  z-index: 50;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.14);
}
</style>
