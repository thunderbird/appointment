<script setup lang="ts">
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useUserStore } from '@/stores/user-store';
import ArtLogo from '@/elements/arts/ArtLogo.vue';
// import UserAvatar from '@/elements/UserAvatar.vue';
import {
  IconMenu2,
  IconX,
  IconHome,
  IconCalendarClock,
  IconCalendarCheck,
  // IconExternalLink,
  IconSettings,
  IconLogout,
} from '@tabler/icons-vue';
import { PrimaryButton } from '@thunderbirdops/services-ui';

// component constants
const user = useUserStore();
const { t } = useI18n();

// component properties
defineProps<{
  navItems: string[], // list of route names that are also lang keys (format: label.<key>), used as nav items
}>();

const mainMenuIcons = computed(() => {
  return {
    'dashboard': IconHome,
    'availability': IconCalendarClock,
    'bookings': IconCalendarCheck,
    'settings': IconSettings,
  }
})

const menuOpen = ref(false);
const myLinkTooltip = ref(t('navBar.shareMyLink'));

function onMenuOpen() {
  menuOpen.value = true;
  document.body.style.overflow = 'hidden'
}

function onMenuClose() {
  menuOpen.value = false;
  document.body.style.overflow = 'inherit'
}

async function copyLink() {
  await navigator.clipboard.writeText(user.myLink);

  myLinkTooltip.value = t('info.copiedToClipboard');

  setTimeout(() => {
    myLinkTooltip.value = t('navBar.shareMyLink');
  }, 2000);
};
</script>

<template>
  <!-- Mobile NavBar -->
  <header class="header-mobile">
    <button
      @click="onMenuOpen"
      :aria-label="t('label.openMenu')"
      :aria-expanded="menuOpen"
      aria-controls="primaryNav"
    >
      <icon-menu2 size="24" />
    </button>

    <router-link
      :to="{ name: user?.authenticated ? 'dashboard' : 'home' }"
    >
      <img src="@/assets/svg/appointment_logo_beta.svg" alt="Appointment Logo" />
    </router-link>
  </header>

  <!-- Navigation Panel -->
  <nav v-if="menuOpen" id="primaryNav">
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
        <router-link
          v-for="navItem in navItems"
          :key="navItem"
          :to="navItem"
        >
          <li>
            <component :is="mainMenuIcons[navItem]" size="24" />
            <span>{{ t(`label.${navItem}`) }}</span>
          </li>
        </router-link>
      </ul>
    </div>

    <div class="menu-footer-container">
      <ul @click="onMenuClose">
        <router-link to="report-bug">
          <li>
            {{ t('navBar.reportBug') }}
          </li>
        </router-link>
        <router-link to="contact">
          <li>
            {{ t('label.contact') }}
          </li>
        </router-link>
        <router-link to="logout">
          <li>
            <icon-logout size="24" />
            {{ t('label.logOut') }}
          </li>
        </router-link>
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
  height: 64px;
  background-color: var(--colour-neutral-base);
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
  position: absolute;
  display: flex;
  flex-direction: column;
  top: 0;
  bottom: 0;
  width: 75%;
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  z-index: 99999;
  background-color: var(--colour-neutral-raised);

  .menu-content-container {
    flex-grow: 1;
    padding: 1rem;

    header {
      display: flex;
      align-items: center;
      height: 32px;
      margin-block-end: 2rem;

      & > svg {
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
  }

  .menu-footer-container {
    padding: 1rem;
    background-color: var(--colour-neutral-base);

    ul {
      display: flex;
      flex-direction: column;
      gap: 1rem;

      li {
        display: flex;
        gap: 0.75rem;
      }
    }
  }
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