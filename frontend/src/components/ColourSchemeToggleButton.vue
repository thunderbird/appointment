<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { PhSun, PhMoon } from '@phosphor-icons/vue';
import { ToolTip } from '@thunderbirdops/services-ui';
import { isDark, toggleColourScheme } from '@/composables/useColourScheme';

const { t } = useI18n();
</script>

<template>
  <tool-tip>
    <button
      class="nav-colour-scheme-toggle-button"
      :class="{ dark: isDark }"
      @click="toggleColourScheme"
      :aria-label="isDark ? t('label.switchToLightTheme') : t('label.switchToDarkTheme')"
    >
      <ph-sun v-if="isDark" :size="24" />
      <ph-moon v-else :size="24" />
    </button>
    <template #content>{{ isDark ? t('label.switchToLightTheme') : t('label.switchToDarkTheme') }}</template>
  </tool-tip>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

@media (--md) {
  .nav-colour-scheme-toggle-button {
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    padding: 0.75rem;
    color: #18181b;

    &.dark {
      color: var(--colour-ti-secondary);
    }
  }
}
</style>
