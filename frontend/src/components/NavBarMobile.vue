<script setup lang="ts">
import { inject, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useUserStore } from '@/stores/user-store';
import {
  PhList,
  PhX,
  PhHouse,
  PhCalendarDot,
  PhCalendarCheck,
  PhArrowSquareOut,
  PhGear,
  PhSignOut,
  PhCaretDown,
  PhUserSquare,
} from '@phosphor-icons/vue';
import { PrimaryButton, UserAvatar } from '@thunderbirdops/services-ui';
import { accountsTbProfileUrlKey } from '@/keys';

// component constants
const userStore = useUserStore();
const { t } = useI18n();

const navItems = [
  { route: 'dashboard', i18nKey: 'dashboard', icon: PhHouse },
  { route: 'bookings', i18nKey: 'bookings', icon: PhCalendarCheck },
  { route: 'availability', i18nKey: 'availability', icon: PhCalendarDot },
  { route: 'settings', i18nKey: 'settings', icon: PhGear },
];

const accountsTbProfileUrl = inject(accountsTbProfileUrlKey);

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
      <ph-list size="24" />
    </button>

    <router-link :to="{ name: userStore.authenticated ? 'dashboard' : 'home' }">
      <img src="@/assets/svg/appointment_logo.svg" alt="Appointment Logo" />
    </router-link>
  </header>

  <!-- Navigation Panel (open) -->
  <nav v-if="menuOpen" id="primaryNav">
    <!-- Scrim/Overlay -->
    <div class="menu-scrim" @click="onMenuClose"></div>

    <div class="menu-content-container">
      <header>
        <button @click="onMenuClose">
          <ph-x size="24" />
        </button>

        <img src="@/assets/svg/appointment_logo.svg" alt="Appointment Logo" />
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
              <user-avatar :username="userStore.data.username" :avatar-url="userStore.data.avatarUrl" />
              <span class="user-email">{{ userStore.data.email }}</span>
            </div>
            <ph-caret-down size="20" class="chevron-icon" />
          </summary>

          <ul @click="onMenuClose">
            <a :href="accountsTbProfileUrl">
              <li>
                <ph-user-square size="24" />
                {{ t('label.userProfile') }}
              </li>
            </a>
            <router-link to="report-bug">
              <li>
                <ph-arrow-square-out size="24" />
                {{ t('navBar.reportBug') }}
              </li>
            </router-link>
            <router-link to="contact">
              <li>
                <ph-arrow-square-out size="24" />
                {{ t('label.contact') }}
              </li>
            </router-link>
          </ul>
        </details>
        <router-link to="logout">
          <ph-sign-out size="24" />
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
  background-color: #1a202c; /* Forced dark mode as we don't have light mode for logo yet */
  color: #eeeef0; /* Forced dark mode as we don't have light mode for logo yet */
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
    background-color: #262d3b; /* Forced dark mode as we don't have light mode for logo yet */
    color: #d9d9de; /* Forced dark mode as we don't have light mode for logo yet */
    z-index: 2;
    padding: 1rem;

    header {
      display: flex;
      align-items: center;
      height: 32px;
      gap: 1rem;
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
      background-color: #1a202c; /* Forced dark mode as we don't have light mode for logo yet */
      color: #eeeef0; /* Forced dark mode as we don't have light mode for logo yet */

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
            min-width: 0;
            flex: 1;

            :deep(.avatar.regular) {
              flex-shrink: 0;
            }

            :deep(.initials) {
              color: #eeeef0; /* Forced dark mode as we don't have light mode for logo yet */
            }

            .user-email {
              font-size: 0.875rem;
              font-weight: 500;
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
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
