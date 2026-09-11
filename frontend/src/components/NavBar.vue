<script setup lang="ts">
import { inject, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user-store';
import NavBarItem from '@/elements/NavBarItem.vue';
import { TooltipPosition } from '@/definitions';
import { PhLinkSimple, PhSun, PhMoon, PhGear, PhWarningCircle } from '@phosphor-icons/vue';
import { ToolTip, BaseButton, SendIcon, MailIcon, AppointmentIcon, AppDrawer, type AppDrawerApp } from '@thunderbirdops/services-ui';
import UserMenu from '@/components/UserMenu.vue';
import { useExternalConnectionsStore } from '@/stores/external-connections-store';
import { mailUrlKey, sendUrlKey, tbProUrlKey } from '@/keys';
import { isDark, toggleColourScheme } from '@/composables/useColourScheme';
import AppointmentLogo from '@/components/AppointmentLogo.vue';

// component constants
const tbProUrl = inject(tbProUrlKey);
const mailUrl = inject(mailUrlKey);
const sendUrl = inject(sendUrlKey);
const user = useUserStore();
const externalConnectionStore = useExternalConnectionsStore();
const route = useRoute();
const { t } = useI18n();

// component properties
interface Props {
  navItems: string[]; // list of route names that are also lang keys (format: label.<key>), used as nav items
}
defineProps<Props>();

const myLinkTooltip = ref(t('label.copyLink'));

const apps: AppDrawerApp[] = [
  { id: 'appointment', name: 'Appointment', icon: AppointmentIcon, current: true },
  { id: 'mail', name: 'Mail', icon: MailIcon, href: mailUrl },
  { id: 'send', name: 'Send', icon: SendIcon, href: sendUrl },
];

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
  <header class="header-desktop" :class="{ dark: isDark }">
    <router-link class="appointment-logo" :to="{ name: user?.authenticated ? 'dashboard' : 'home' }">
      <appointment-logo />
    </router-link>

    <template v-if="user?.authenticated">
      <nav class="nav-items-container">
        <nav-bar-item
          v-for="item in navItems"
          :key="item"
          :active="isNavEntryActive(item)"
          :label="item === 'dashboard' ? t('label.calendar') : t(`label.${item}`)"
          :link-name="item"
        />
      </nav>

      <div class="nav-items-right-container">
        <div v-if="user.myLink" class="nav-copy-link-button-container">
          <button class="nav-copy-link-button" @click="copyLink" aria-labelledby="copy-meeting-link-button">
            <ph-link-simple id="copy-meeting-link-button" :size="24" />
            <tool-tip :position="TooltipPosition.Top" class="nav-copy-link-tooltip">
              {{ myLinkTooltip }}
            </tool-tip>
          </button>
        </div>

        <router-link
          :to="{ name: 'settings' }"
          class="nav-settings-button"
          :class="{ active: isNavEntryActive('settings') }"
          :aria-label="t('label.settings')"
        >
          <ph-gear :size="24" />
          <ph-warning-circle v-if="externalConnectionStore.hasUnhealthyConnections" class="warning-icon" weight="fill" />
        </router-link>

        <button
          class="nav-colour-scheme-toggle-button"
          @click="toggleColourScheme"
          :aria-label="isDark ? t('label.switchToLightTheme') : t('label.switchToDarkTheme')"
        >
          <ph-sun v-if="isDark" :size="24" />
          <ph-moon v-else :size="24" />
        </button>

        <app-drawer :apps="apps" />

        <user-menu :username="user.data.username" :avatar-url="user.data.avatarUrl" />
      </div>
    </template>

    <template v-else>
      <div class="nav-items-right-container">
        <button
          class="nav-colour-scheme-toggle-button"
          @click="toggleColourScheme"
          :aria-label="isDark ? t('label.switchToLightTheme') : t('label.switchToDarkTheme')"
        >
          <ph-sun v-if="isDark" :size="24" />
          <ph-moon v-else :size="24" />
        </button>

        <a :href="tbProUrl">
          <base-button type="brand" variant="outline" class="learn-more-button">{{ t('label.learnMore') }}</base-button>
        </a>
      </div>
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
    background-color: #f7f7f8;
    box-shadow: 0 8px 24px 0 rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(12px);
    overflow: visible;
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

  .nav-colour-scheme-toggle-button {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.5rem;
    color: #18181b;
  }

  .nav-settings-button {
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    padding: 0.5rem;
    color: #18181b;

    .warning-icon {
      position: absolute;
      top: -0.25rem;
      right: -0.25rem;
      color: var(--colour-danger-default);
      width: 1rem;
      height: 1rem;
    }
  }

  .nav-copy-link-button {
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    padding: 0.5rem;
    color: #18181b;

    &:active {
      color: var(--colour-accent-teal);
    }
  }

  :deep(.app-drawer__button svg) {
    width: 1.5rem;
    height: 1.5rem;
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
    svg {
      height: 3rem;
      width: auto;
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

.header-desktop.dark {
  background-color: #111113;
}

.header-desktop.dark .nav-copy-link-button,
.header-desktop.dark .nav-colour-scheme-toggle-button,
.header-desktop.dark .nav-settings-button {
  color: var(--colour-ti-secondary);
}
</style>
