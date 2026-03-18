<script setup lang="ts">
import { ref } from 'vue';
import { vOnClickOutside } from '@vueuse/components';

const open = ref(false);
const toggle = () => { open.value = !open.value; };
const close = () => { open.value = false; };

defineExpose({ close });
</script>

<template>
  <div class="drop-down-wrapper" v-on-click-outside="close">
    <div class="trigger" @click="toggle">
      <slot name="trigger"></slot>
    </div>
    <transition>
      <div v-show="open" class="drop-down">
        <slot></slot>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.drop-down-wrapper {
  position: relative;

  .trigger {
    cursor: pointer;
    user-select: none;
  }

  .drop-down {
    position: absolute;
    right: 0;
  }
}
</style>
