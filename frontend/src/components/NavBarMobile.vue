<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user-store';
import UserAvatar from '@/elements/UserAvatar.vue';
import DropDown from '@/elements/DropDown.vue';
import NavBarItem from '@/elements/NavBarItem.vue';
import TextButton from '@/elements/TextButton.vue';
import { TooltipPosition } from '@/definitions';
import { IconExternalLink, IconLink } from '@tabler/icons-vue';
import { ToolTip } from '@thunderbirdops/services-ui';

// component constants
const user = useUserStore();
const route = useRoute();
const { t } = useI18n();

// component properties
interface Props {
  navItems: string[], // list of route names that are also lang keys (format: label.<key>), used as nav items
}
defineProps<Props>();

const profileDropdown = ref();
const myLinkTooltip = ref(t('label.copyLink'));

/**
 * Is this nav entry active?
 * @param item
 */
const isNavEntryActive = (item: string) => {
  // Hack for FTUE!
  if (item === 'dashboard' && route.name === 'setup') {
    return true;
  }
  return route.name === item;
};

// Link copy
const copyLink = async () => {
  await navigator.clipboard.writeText(user.myLink);

  myLinkTooltip.value = t('info.copiedToClipboard');

  setTimeout(() => {
    myLinkTooltip.value = t('label.copyLink');
  }, 2000);
};

</script>

<template>
  <!-- Mobile NavBar -->
  <header class="header-mobile">
    hi
  </header>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.header-mobile {
  height: 64px;
  background-color: var(--colour-neutral-base);
}

@media (--md) {
  /* Hide header mobile in favor of desktop */
  .header-mobile {
    display: none;
  }
}

@media (prefers-reduced-motion: no-preference) {
  .header-mobile {
    transition: opacity 250ms ease-out;
  }
}
</style>