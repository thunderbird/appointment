<template>
  <transition
    enter-active-class="dropdown-enter-active"
    enter-from-class="dropdown-enter-from"
    enter-to-class="dropdown-enter-to"
    leave-active-class="dropdown-leave-active"
    leave-from-class="dropdown-leave-from"
    leave-to-class="dropdown-leave-to"
  >
    <slot />
  </transition>
</template>

<style scoped>
.dropdown-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.dropdown-enter-to {
  opacity: 1;
  transform: scale(1);
}

.dropdown-leave-from {
  opacity: 1;
  transform: scale(1);
}

.dropdown-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

@media (prefers-reduced-motion: no-preference) {
  .dropdown-enter-active {
    transition: all 0.2s ease-out;
  }

  .dropdown-leave-active {
    transition: all 0.15s ease-in;
  }
}
</style>