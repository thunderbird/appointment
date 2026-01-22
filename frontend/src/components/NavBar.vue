<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user-store';
import NavBarItem from '@/elements/NavBarItem.vue';
import { TooltipPosition } from '@/definitions';
import { PhLinkSimple } from '@phosphor-icons/vue';
import { ToolTip, BaseButton } from '@thunderbirdops/services-ui';
import UserMenu from '@/components/UserMenu.vue';

// component constants
const tbProUrl = import.meta.env.VITE_TB_PRO_URL;
const user = useUserStore();
const route = useRoute();
const { t } = useI18n();

// component properties
interface Props {
  navItems: string[], // list of route names that are also lang keys (format: label.<key>), used as nav items
}
defineProps<Props>();

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
  <header class="header-desktop">
    <router-link
      class="appointment-logo"
      :to="{ name: user?.authenticated ? 'dashboard' : 'home' }"
    >
      <img src="@/assets/svg/appointment_logo.svg" alt="Appointment Logo" />
    </router-link>

    <template v-if="user?.authenticated">
      <nav class="nav-items-container">
        <nav-bar-item
          v-for="item in navItems"
          :key="item"
          :active="isNavEntryActive(item)"
          :label="t(`label.${item}`)"
          :link-name="item"
        />
      </nav>

      <div class="nav-items-right-container">
        <div v-if="user.myLink" class="nav-copy-link-button-container">
          <button
            class="nav-copy-link-button"
            @click="copyLink"
            aria-labelledby="copy-meeting-link-button"
          >
            <ph-link-simple id="copy-meeting-link-button" :size="24" />
            <tool-tip
              :position="TooltipPosition.Top"
              class="nav-copy-link-tooltip"
            >
              {{ myLinkTooltip }}
            </tool-tip>
          </button>
        </div>

        <user-menu :username="user.data.username" :avatar-url="user.data.avatarUrl" />
      </div>
    </template>

    <template v-else>
      <a :href="tbProUrl">
        <base-button type="brand" variant="outline" class="learn-more-button">{{ t('label.learnMore') }}</base-button>
      </a>
    </template>
  </header>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

/* Hide header desktop in favor of mobile */
.header-desktop {
  display: none;
}

/* Override default avatar styles from services-ui */
:deep(.avatar.regular) {
  span {
    font-weight: 600;
    font-size: 0.875rem;
    color: var(--colour-ti-base-dark);
  }
}

:deep(.learn-more-button.base.brand.outline) {
  height: 2.25rem;
  font-family: metropolis;
  font-size: 0.8125rem;
  padding: 0.875rem 1rem;
  letter-spacing: 0.65px;
  color: var(--colour-ti-base-dark);
}

@media (--md) {
  .header-desktop {
    position: fixed;
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    height: 68px;
    padding-inline: 1rem;
    box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    overflow: visible;
    background-image: linear-gradient(to top, #1a202c, #1c3f47); /* one-off colours to approximate Zeplin gradient */
    z-index: 50;
  }

  nav {
    display: flex;
    align-items: stretch;
    gap: 1rem;
  }

  .nav-items-container {
    display: flex;
    align-items: center;
    justify-content: end;
    gap: 0.5rem;
    height: 100%;
  }

  .nav-items-right-container {
    display: flex;
    align-items: center;
    gap: 1.5rem;
  }

  .nav-copy-link-button {
    font-weight: 600;
    display: flex;
    align-items: center;
    position: relative;
    color: #f3f4f6; /* TODO: hard-coded as we don't have light mode for NavBar yet */

    &:active {
      color: var(--colour-accent-teal);
    }
  }

  .nav-copy-link-tooltip {
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

  .nav-copy-link-button:hover .nav-copy-link-tooltip {
    opacity: 1;
    pointer-events: auto;
  }

  .appointment-logo {
    img {
      height: 2.25rem;
    }
  }
}

@media (--lg) {
  .header-desktop {
    padding-inline: 3.5rem;
  }
}

@media (prefers-reduced-motion: no-preference) {
  .nav-copy-link-tooltip {
    transition: opacity 250ms ease-out;
  }
}
</style>
