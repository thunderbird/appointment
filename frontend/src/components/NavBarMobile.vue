<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useUserStore } from '@/stores/user-store';
import {
  PhList,
  PhX,
  PhHouse,
  PhCalendarDot,
  PhCalendarCheck,
  PhSun,
  PhMoon,
} from '@phosphor-icons/vue';
import { PrimaryButton, SettingsIcon } from '@thunderbirdops/services-ui';
import UserMenu from '@/components/UserMenu.vue';
import { isDark, toggleColourScheme } from '@/composables/useColourScheme';
import AppointmentLogo from '@/components/AppointmentLogo.vue';

// component constants
const userStore = useUserStore();
const { t } = useI18n();

const navItems = [
  { route: 'dashboard', i18nKey: 'calendar', icon: PhHouse },
  { route: 'bookings', i18nKey: 'bookings', icon: PhCalendarCheck },
  { route: 'availability', i18nKey: 'availability', icon: PhCalendarDot },
  { route: 'settings', i18nKey: 'settings', icon: SettingsIcon },
];

const menuOpen = ref(false);
const myLinkTooltip = ref(t('navBar.shareMyLink'));

function onMenuOpen() {
  menuOpen.value = true;
  // Hide body scroll when the menu is open so content underneath is not scrollable
  document.body.style.overflow = 'hidden';
}

function onMenuClose() {
  menuOpen.value = false;
  document.body.style.overflow = 'inherit';
}

async function copyLink() {
  await navigator.clipboard.writeText(userStore.myLink);

  myLinkTooltip.value = t('info.copiedToClipboard');

  setTimeout(() => {
    myLinkTooltip.value = t('navBar.shareMyLink');
  }, 2000);
}
</script>

<template>
  <!-- Mobile NavBar (closed) -->
  <header class="header-mobile" :class="{ dark: isDark }">
    <router-link class="appointment-logo" :to="{ name: userStore.authenticated ? 'dashboard' : 'home' }">
      <appointment-logo />
    </router-link>

    <div class="header-mobile-right">
      <button class="menu-button" @click="onMenuOpen" :aria-label="t('label.openMenu')" :aria-expanded="menuOpen" aria-controls="primaryNav">
        <ph-list size="24" />
      </button>

      <user-menu v-if="userStore.authenticated" :username="userStore.data.username" :avatar-url="userStore.data.avatarUrl" />
    </div>
  </header>

  <!-- Navigation Panel (open) -->
  <nav v-if="menuOpen" id="primaryNav">
    <!-- Scrim/Overlay -->
    <div class="menu-scrim" @click="onMenuClose"></div>

    <div class="menu-content-container" :class="{ dark: isDark }">
      <header>
        <button @click="onMenuClose" :aria-label="t('label.closeMenu')">
          <ph-x size="24" />
        </button>
      </header>

      <primary-button @click="copyLink" class="share-link-button">
        {{ myLinkTooltip }}
      </primary-button>

      <ul @click="onMenuClose">
        <template v-for="navItem in navItems" :key="navItem.route">

          <li v-if="navItem.route === 'settings'">
            <button class="theme-toggle" @click.stop="toggleColourScheme">
              <ph-sun v-if="isDark" size="24" />
              <ph-moon v-else size="24" />
              <span>{{ t('label.switchTheme') }}</span>
            </button>
          </li>

          <router-link :to="navItem.route">
            <li>
              <component :is="navItem.icon" size="24" />
              <span>{{ t(`label.${navItem.i18nKey}`) }}</span>
            </li>
          </router-link>
        </template>
      </ul>
    </div>
  </nav>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.header-mobile {
  position: sticky;
  top: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 64px;
  background-color: #f7f7f8;
  color: #18181b;
  box-shadow: 0 8px 24px 0 rgba(0, 0, 0, 0.1);
  padding: 0.5rem 1rem;
  z-index: 9999;

  &.dark {
    background-color: #111113;
    color: #eeeef0;
  }

  .appointment-logo svg {
    height: 3rem;
    width: auto;
  }

  .header-mobile-right {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .menu-button {
    padding: 0.75rem; /* 48px touch target */
    color: inherit;
  }
}

nav {
  position: fixed;
  display: flex;
  flex-direction: column;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 99999;

  .menu-scrim {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 1;
  }

  .menu-content-container {
    position: relative;
    display: flex;
    flex-direction: column;
    width: 75%;
    height: 100%;
    margin-inline-start: auto; /* Open from the right */
    box-shadow:
      0 10px 15px -3px rgb(0 0 0 / 0.1),
      0 4px 6px -4px rgb(0 0 0 / 0.1);
    background-color: #f7f7f8;
    color: #18181b;
    z-index: 2;
    padding: 1rem;

    &.dark {
      background-color: #111113;
      color: #eeeef0;
    }

    header {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      height: 32px;
      gap: 1rem;
      margin-block-end: 2rem;
    }

    .share-link-button {
      width: 100%;
      margin-block-end: 1.5rem;
    }

    ul {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;

      li {
        display: flex;
        gap: 0.75rem;
        padding-block: 0.5rem;
      }

      .theme-toggle {
        display: flex;
        gap: 0.75rem;
        padding: 0;
        font: inherit;
        color: inherit;
        cursor: pointer;
      }
    }
  }
}

@media (--md) {
  /* Hide header mobile in favor of desktop */
  .header-mobile {
    display: none;
  }

  nav {
    display: none;
  }
}

@media (prefers-reduced-motion: no-preference) {
  .header-mobile {
    transition: opacity 250ms ease-out;
  }
}
</style>
