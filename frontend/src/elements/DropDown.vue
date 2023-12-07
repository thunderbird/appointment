<template>
  <div class="relative" v-on-click-outside="close">
    <div class="cursor-pointer select-none" @click="toggle">
      <slot name="trigger"></slot>
    </div>
    <transition>
      <div v-show="open" class="absolute right-0" @click="close">
        <slot></slot>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { vOnClickOutside } from '@vueuse/components';

const open = ref(false);
const toggle = () => { open.value = !open.value; };
const close = () => { open.value = false; };
</script>
