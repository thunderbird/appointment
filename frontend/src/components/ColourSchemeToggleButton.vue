<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { PhSun, PhMoon } from '@phosphor-icons/vue';
import { ToolTip } from '@thunderbirdops/services-ui';
import { TooltipPosition } from '@/definitions';
import { isDark, toggleColourScheme } from '@/composables/useColourScheme';

const { t } = useI18n();
</script>

<template>
  <button
    class="nav-colour-scheme-toggle-button"
    :class="{ dark: isDark }"
    @click="toggleColourScheme"
    :aria-label="isDark ? t('label.switchToLightTheme') : t('label.switchToDarkTheme')"
  >
    <ph-sun v-if="isDark" :size="24" />
    <ph-moon v-else :size="24" />
    <tool-tip :position="TooltipPosition.Top" class="nav-tooltip">
      {{ isDark ? t('label.switchToLightTheme') : t('label.switchToDarkTheme') }}
    </tool-tip>
  </button>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.nav-tooltip {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 0.5rem;
  opacity: 0;
  white-space: nowrap;
  font-size: 0.75rem;
  min-width: max-content;
  pointer-events: none;
}

@media (prefers-reduced-motion: no-preference) {
  .nav-tooltip {
    transition: opacity 250ms ease-out;
  }
}

@media (--md) {
  .nav-colour-scheme-toggle-button {
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    padding: 0.5rem;
    color: #18181b;

    &.dark {
      color: var(--colour-ti-secondary);
    }

    &:hover .nav-tooltip {
      opacity: 1;
      pointer-events: auto;
    }
  }
}
</style>
