<template>
  <div class="tooltip" :aria-label="alt">
    <div class="tooltip-container">
      <div class="tooltip-body">
        <slot></slot>
      </div>
      <svg class="beak" :class="position" width="28" height="6" viewBox="0 0 28 6" fill="none" xmlns="http://www.w3.org/2000/svg">
        <g>
          <path d="M15.4142 4.58579C14.6332 5.36683 13.3668 5.36683 12.5858 4.58579L8 0L20 0L15.4142 4.58579Z" fill="currentColor"/>
        </g>
      </svg>
    </div>
  </div>
</template>

<script setup>
// component properties
import { tooltipPosition } from '@/definitions';

defineProps({
  alt: String, // Tooltip text
  position: {
    type: tooltipPosition,
    default: tooltipPosition.bottom,
  },
});
</script>

<style scoped>
/*

      pointer-events-none absolute bottom-full z-50 -translate-y-2 whitespace-nowrap text-wrap rounded-lg bg-black/75 px-3
      py-1.5 font-sans text-sm font-normal text-white focus:outline-none
 */
.tooltip {
  position: absolute;
  text-wrap: wrap;
  border-radius: 0.25rem;
  background-color: var(--surface-subtle);
  font-family: 'Inter', sans-serif;
  color: var(--tbpro-text);
  z-index: 100;
  box-shadow: 0px 4px 8px 0px rgba(0, 0, 0, 0.14), 0px 0px 2px 0px rgba(0, 0, 0, 0.12);
}

.tooltip-body {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0.25rem 0.5rem;

}

.tooltip-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;

}

/*
absolute left-1/2 top-full size-3 -translate-x-1/2 fill-black/75
 */
.beak {
  position: absolute;
  color: var(--surface-subtle);
}

.pos-none {
  display: none;
}

.pos-top {
  top: -6px;
  transform: scaleY(-1)
}

.pos-bottom {
  top: 100%;
}

.pos-left {
  left: -17px;
  transform: rotateZ(90deg);
}

.pos-right {
  right: -17px;
  transform: rotateZ(-90deg);
}
</style>
