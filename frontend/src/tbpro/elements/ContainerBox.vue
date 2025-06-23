<template>
  <div class="container-box">
    <slot></slot>
  </div>
</template>

<style scoped>
.container-box {
  position: relative;
  text-wrap: wrap;
  border-radius: 0.25rem;
  background-color: var(--colour-neutral-base);
  font-family: 'Inter', sans-serif;
  color: var(--colour-ti-base);
  padding: .75rem .75rem;
  z-index: 50;
  box-shadow: 0px 2px 4px 2px rgba(0, 0, 0, 0.14), 0px 0px 2px 0px rgba(0, 0, 0, 0.12);
}
</style>
