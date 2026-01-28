<template>
  <div class="loading-spinner"></div>
</template>

<style scoped>
.loading-spinner {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  border-width: 4px;
  border-style: solid;
  border-color: var(--colour-neutral-border);
  border-top-color: var(--colour-primary-default);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
