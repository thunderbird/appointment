<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useUserStore } from '@/stores/user-store';
import ArtLogo from '@/elements/arts/ArtLogo.vue';
import UserAvatar from '@/elements/UserAvatar.vue';
import {
  IconMenu2,
  IconX,
  IconHome,
  IconCalendarClock,
  IconCalendarCheck,
  IconExternalLink,
  IconSettings,
  IconLogout,
  IconChevronDown,
  IconUserSquare,
} from '@tabler/icons-vue';
import { PrimaryButton } from '@thunderbirdops/services-ui';

// component constants
const userStore = useUserStore();
const { t } = useI18n();

const navItems = [
  { route: 'dashboard', i18nKey: 'dashboard', icon: IconHome },
  { route: 'bookings', i18nKey: 'bookings', icon: IconCalendarCheck },
  { route: 'availability', i18nKey: 'availability', icon: IconCalendarClock },
  { route: 'settings', i18nKey: 'settings', icon: IconSettings },
];

const menuOpen = ref(false);
const myLinkTooltip = ref(t('navBar.shareMyLink'));

function onMenuOpen() {
  menuOpen.value = true;
  // Hide body scroll when the menu is open so content underneath is not scrollable
  document.body.style.overflow = 'hidden'
}

function onMenuClose() {
  menuOpen.value = false;
  document.body.style.overflow = 'inherit'
}

async function copyLink() {
  await navigator.clipboard.writeText(userStore.myLink);

  myLinkTooltip.value = t('info.copiedToClipboard');

  setTimeout(() => {
    myLinkTooltip.value = t('navBar.shareMyLink');
  }, 2000);
};
</script>

<template>
  <!-- Mobile NavBar (closed) -->
  <header class="header-mobile">
    <button @click="onMenuOpen" :aria-label="t('label.openMenu')" :aria-expanded="menuOpen" aria-controls="primaryNav">
      <icon-menu2 size="24" />
    </button>

    <router-link :to="{ name: userStore.authenticated ? 'dashboard' : 'home' }">
      <img src="@/assets/svg/appointment_logo_beta.svg" alt="Appointment Logo" />
    </router-link>
  </header>

  <!-- Navigation Panel (open) -->
  <nav v-if="menuOpen" id="primaryNav">
    <!-- Scrim/Overlay -->
    <div class="menu-scrim" @click="onMenuClose"></div>

    <div class="menu-content-container">
      <header>
        <button @click="onMenuClose">
          <icon-x size="24" />
        </button>

        <art-logo />
      </header>

      <primary-button @click="copyLink" class="share-link-button">
        {{ myLinkTooltip }}
      </primary-button>

      <ul @click="onMenuClose">
        <router-link v-for="navItem in navItems" :key="navItem.route" :to="navItem.route">
          <li>
            <component :is="navItem.icon" size="24" />
            <span>{{ t(`label.${navItem.i18nKey}`) }}</span>
          </li>
        </router-link>
      </ul>

      <div class="menu-footer-container">
        <details class="footer-accordion">
          <summary class="footer-header">
            <div class="user-info">
              <user-avatar />
              <span class="user-email">{{ userStore.data.email }}</span>
            </div>
            <icon-chevron-down size="20" class="chevron-icon" />
          </summary>

          <ul @click="onMenuClose">
            <router-link to="profile">
              <li>
                <icon-user-square size="24" />
                {{ t('label.userProfile') }}
              </li>
            </router-link>
            <router-link to="report-bug">
              <li>
                <icon-external-link size="24" />
                {{ t('navBar.reportBug') }}
              </li>
            </router-link>
            <router-link to="contact">
              <li>
                <icon-external-link size="24" />
                {{ t('label.contact') }}
              </li>
            </router-link>
          </ul>
        </details>
        <router-link to="logout">
          <icon-logout size="24" />
          {{ t('label.logOut') }}
        </router-link>
      </div>
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
  min-height: 64px;
  background-color: var(--colour-neutral-base);
  color: var(--colour-ti-secondary);
  padding: 0.5rem;
  z-index: 9999;

  button {
    padding: 0.5rem;
    z-index: 9999;
  }

  a {
    position: absolute;
    left: 0;
    right: 0;

    img {
      height: 2rem;
      margin: 0 auto;
    }
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
    box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    background-color: var(--colour-neutral-raised);
    color: var(--colour-ti-secondary);
    z-index: 2;
    padding: 1rem;

    header {
      display: flex;
      align-items: center;
      height: 32px;
      margin-block-end: 2rem;

      &>svg {
        height: 48px;
        width: min-content;
        margin: 0 auto;
      }
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
    }

    .menu-footer-container {
      margin-top: auto;
      margin-left: -1rem;
      margin-right: -1rem;
      margin-bottom: -1rem;
      padding: 1rem;
      background-color: var(--colour-neutral-base);

      .footer-accordion {
        .footer-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          cursor: pointer;
          padding: 0.5rem 0;

          .user-info {
            display: flex;
            align-items: center;
            gap: 0.75rem;

            .user-email {
              font-size: 0.875rem;
              color: var(--colour-ti-base);
              font-weight: 500;
            }
          }
        }

        &[open] .footer-header .chevron-icon {
          transform: rotate(180deg);
        }

        ul {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          padding-block-start: 0.75rem;

          li {
            display: flex;
            gap: 0.75rem;
          }
        }
      }

      > a {
        display: flex;
        gap: 0.75rem;
        padding: 0.5rem 0;
        margin-top: 1rem;
        text-decoration: none;
        color: inherit;
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