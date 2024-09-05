<script setup lang="ts">
// component properties
import { TooltipPosition } from '@/definitions';

// component properties
interface Props {
  alt?: string;
  position?: TooltipPosition;
};
withDefaults(defineProps<Props>(), {
  alt: '',
  position: TooltipPosition.Bottom,
})
</script>

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

<style scoped>
.tooltip {
  position: absolute;
  text-wrap: wrap;
  border-radius: 0.25rem;
  background-color: var(--colour-neutral-subtle);
  font-family: 'Inter', sans-serif;
  color: var(--colour-ti-base);
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

.beak {
  position: absolute;
  color: var(--colour-neutral-subtle);
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
