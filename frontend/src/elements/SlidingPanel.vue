<script setup lang="ts">
import { computed } from 'vue'
import { IconX } from '@tabler/icons-vue'

interface Props {
  open: boolean
  title?: string
  closeOnScrimClick?: boolean
}

interface Emits {
  (e: 'update:open', value: boolean): void
  (e: 'close'): void
}

const props = withDefaults(defineProps<Props>(), {
  closeOnScrimClick: true
})

const emit = defineEmits<Emits>()

const isOpen = computed({
  get: () => props.open,
  set: (value) => emit('update:open', value)
})

const handleClose = () => {
  isOpen.value = false
  emit('close')
}

const handleScrimClick = () => {
  if (props.closeOnScrimClick) {
    handleClose()
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="scrim">
      <div
        v-if="isOpen"
        class="scrim"
        @click="handleScrimClick"
      />
    </Transition>
    <Transition name="panel">
      <div v-if="isOpen" class="sliding-panel" @click.stop>
        <!-- Header -->
        <div class="header">
          <div class="title">
            <slot name="title">
              {{ title }}
            </slot>
          </div>
          <button
            class="close-btn"
            @click="handleClose"
            aria-label="Close panel"
          >
            <icon-x />
          </button>
        </div>

        <!-- Content -->
        <div class="content">
          <slot />
        </div>

        <!-- CTA Container -->
        <div v-if="$slots.cta" class="cta-container">
          <slot name="cta" />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.scrim {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.sliding-panel {
  position: fixed;
  top: 0;
  right: 0;
  background-color: var(--colour-neutral-base);
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  width: 600px;
  height: 100vh;
  overflow: hidden;
  z-index: 1001;
}

/* Panel transition */
.panel-enter-active,
.panel-leave-active {
  transition: transform 0.3s ease;
}

.panel-enter-from,
.panel-leave-to {
  transform: translateX(100%);
}

.panel-enter-to,
.panel-leave-from {
  transform: translateX(0);
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--colour-neutral-border);
  background-color: var(--colour-neutral-lower);
  flex-shrink: 0;
}

.title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--colour-ti-base);
  flex: 1;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  border-radius: 6px;
  color: var(--colour-ti-muted);
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;

  &:hover {
    background-color: var(--colour-neutral-subtle);
    color: var(--colour-ti-secondary);
  }

  &:focus {
    outline: 2px solid var(--colour-primary-default);
    outline-offset: 2px;
  }
}

.content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.cta-container {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--colour-neutral-border);
  background-color: var(--colour-neutral-lower);
  flex-shrink: 0;
}

/* Scrim transition */
.scrim-enter-active,
.scrim-leave-active {
  transition: opacity 0.3s ease;
}

.scrim-enter-from,
.scrim-leave-to {
  opacity: 0;
}


</style>
