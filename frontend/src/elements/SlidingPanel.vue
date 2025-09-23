<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import { PhX } from '@phosphor-icons/vue'

const { t } = useI18n();

const props = withDefaults(defineProps<{
  title?: string
  closeOnScrimClick?: boolean
  side?: 'left' | 'right'
}>(), {
  closeOnScrimClick: true,
  side: 'right'
})

const emit = defineEmits<{
  (e: 'open'): void
  (e: 'close'): void
}>()

const panelRef = useTemplateRef<HTMLDialogElement>('panel')
const contentRef = useTemplateRef<HTMLDivElement>('content')

const panelClasses = computed(() => [
  'sliding-panel',
  `sliding-panel--${props.side}-side`
])

const headerClasses = computed(() => [
  'header',
  `header--${props.side}-side`
])

const handleDialogClick = (event: MouseEvent) => {
  if (event.target === panelRef.value && props.closeOnScrimClick) {
    closePanel()
  }
}

const closePanel = () => {
  // Calling the HTML dialog's close method
  // https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dialog#methods
  panelRef.value?.close()

  emit('close')
}

const showPanel = () => {
  // Calling the HTML dialog's showModal method
  // https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dialog#methods
  panelRef.value?.showModal()

  emit('open')
}

const focusOnContentTop = () => {
  const firstFocusableElement = contentRef.value?.querySelector<HTMLElement>(
    'button, [href], input, select, textarea, [tabindex]'
  )

  if (firstFocusableElement) {
    firstFocusableElement.focus();
  }
}

defineExpose({
  showPanel,
  closePanel
})
</script>

<template>
  <dialog ref="panel" :class="panelClasses" @click="handleDialogClick" autofocus>
    <!-- Header -->
    <div :class="headerClasses">
      <div class="title">
        <slot name="title">
          {{ title }}
        </slot>
      </div>
      <button
        class="close-btn"
        @click="closePanel"
        :aria-label="t('label.closePanel')"
      >
        <ph-x size="24" />
      </button>
    </div>

    <!-- Content -->
    <div ref="content" class="content" tabindex="-1">
      <slot />

      <button
        class="screen-reader-only"
        @click="focusOnContentTop"
        :aria-label="t('label.backToTop')"
      />

      <slot name="cta" />
    </div>
  </dialog>
</template>

<style scoped>
.sliding-panel {
  /* Override browser defaults */
  max-height: 100dvh;
  max-width: 100dvw;  

  &[open] {
    display: flex;
    flex-direction: column;
    height: 100dvh;
    width: 100%;
    max-width: 600px;
    transform: translateX(0);
  }

  &.sliding-panel--right-side {
    margin: 0 0 0 auto;
  }

  &.sliding-panel--left-side {
    margin: 0 auto 0 0;
  }

  &::backdrop {
    background-color: rgba(0, 0, 0, 0.7);
  }
}

@media (prefers-reduced-motion: no-preference) {
  .sliding-panel {
    &[open] {
      animation: panel-slide-in 0.3s ease;
    }

    &::backdrop {
      animation: backdrop-fade-in 0.3s ease forwards;
    }
  }
}

@keyframes panel-slide-in {
  0% {
    display: none;
    transform: translateX(100%);
  }

  100% {
    display: flex;
    transform: translateX(0);
  }
}

@keyframes backdrop-fade-in {
  0% {
    background-color: rgba(0, 0, 0, 0);
  }

  100% {
    background-color: rgba(0, 0, 0, 0.7);
  }
}

.header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 2rem 1.5rem 2.25rem 1.5rem;
  background-color: var(--colour-neutral-base);
  flex-shrink: 0;

  &.header--right-side {
    flex-direction: row;
  }

  &.header--left-side {
    flex-direction: row-reverse;
  }
}

.title {
  font-size: 1.5rem;
  font-weight: 500;
  font-family: metropolis;
  color: var(--colour-ti-base);
  flex: 1;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 999px;
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
  padding-inline: 1.5rem;
  background-color: var(--colour-neutral-base);
}
</style>
