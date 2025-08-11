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

  <!-- Desktop NavBar -->
  <header class="header-desktop">
    <router-link
      class="appointment-logo"
      :to="{ name: user?.authenticated ? 'dashboard' : 'home' }"
    >
      <img src="@/assets/svg/appointment_logo_beta.svg" alt="Appointment Logo" />
    </router-link>
    <nav v-if="user.authenticated">
      <div class="nav-items-container">
        <nav-bar-item
          v-for="item in navItems"
          :key="item"
          :active="isNavEntryActive(item)"
          :label="t(`label.${item}`)"
          :link-name="item"
        />
        <div v-if="user.myLink" class="nav-copy-link-button-container">
          <button
            class="nav-copy-link-button"
            @click="copyLink"
            aria-labelledby="copy-meeting-link-button"
          >
            <icon-link id="copy-meeting-link-button"></icon-link>
            <tool-tip
              :position="TooltipPosition.Top"
              class="nav-copy-link-tooltip"
            >
              {{ myLinkTooltip }}
            </tool-tip>
          </button>
        </div>
      </div>

      <drop-down class="user-dropdown" ref="profileDropdown">
        <template #trigger>
          <div class="user-dropdown-trigger-container">
            <span>
              {{ user.data.email }}
            </span>

            <user-avatar />
          </div>
        </template>
        <template #default>
          <div
            @click="profileDropdown.close()"
            class="user-dropdown-content-container"
          >
            <router-link :to="{ name: 'profile' }">
              {{ t('label.userProfile') }}
            </router-link>
            <text-button
              v-show="user.myLink"
              uid="myLink"
              :label="t('navBar.shareMyLink')"
              :copy="user.myLink"
              :title="t('label.copy')"
              class="share-link-button"
              data-testid="user-nav-share-link-btn"
            />
            <router-link :to="{ name: 'report-bug' }" class="router-link-with-icon" data-testid="user-nav-report-bug-menu">
              {{ t('navBar.reportBug') }} <icon-external-link class="size-4"/>
            </router-link>
            <router-link :to="{ name: 'contact' }" class="router-link-with-icon" data-testid="user-nav-contact-menu">
              {{ t('label.contact') }} <icon-external-link class="size-4"/>
            </router-link>
            <hr class="border-teal-500" />
            <router-link :to="{ name: 'logout' }" data-testid="user-nav-logout-menu">
              {{ t('label.logOut') }}
            </router-link>
          </div>
        </template>
      </drop-down>
    </nav>
  </header>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

/* Hide header desktop in favor of mobile */
.header-desktop {
  display: none;
}

.header-mobile {
  height: 64px;
  background-color: var(--colour-neutral-base);
}

@media (--md) {
  /* Hide header mobile in favor of desktop */
  .header-mobile {
    display: none;
  }

  .header-desktop {
    position: fixed;
    display: flex;
    justify-content: space-between;
    width: 100%;
    height: 64px;
    padding-inline: 1rem;
    box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    overflow: visible;
    border-block-end: 1px solid var(--colour-neutral-border);
    background-color: var(--colour-neutral-base);
    z-index: 50;
  }

  nav {
    display: flex;
    align-items: stretch;
    gap: 1rem;
  }

  .nav-items-container {
    display: flex;
    justify-content: end;
    gap: 2rem;
  }

  .nav-copy-link-button-container {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    padding-inline: 1rem;
  }

  .nav-copy-link-button {
    font-weight: 600;
    display: flex;
    align-items: center;
    position: relative;

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
    flex-shrink: 0;
    border-inline-end: 1px solid var(--colour-neutral-border);
    padding: 1rem 2rem 1rem 1rem;

    img {
      height: 2rem;
    }
  }

  .user-dropdown {
    align-self: center;
  }

  .user-dropdown-trigger-container {
    display: flex;
    align-items: center;
    gap: 1rem;
    border: 1px solid var(--colour-neutral-border);
    border-radius: 0.375rem;
    background-color: white;
    padding: 0.25rem 0.25rem 0.25rem 0.75rem;

    & > span {
      font-size: 0.875rem;
      color: var(--colour-ti-muted);
    }
  }

  .user-dropdown-content-container {
    position: static;
    left: auto;
    top: auto;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    width: 12rem;
    border-radius: 0.375rem;
    background-color: var(--colour-neutral-raised);
    padding: 1rem;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);

    a {
      padding: 0.5rem;
    }

    .share-link-button {
      flex-direction: row-reverse;
      justify-content: space-between;
      border: none;
      font-size: 1rem;
      font-weight: 400;
      line-height: 1.5rem;
      color: inherit;
      padding: 0.5rem;

      &:hover {
        background-color: inherit;
        box-shadow: none;
      }
    }

    .router-link-with-icon {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
  }
}

@media (prefers-reduced-motion: no-preference) {
  .nav-copy-link-tooltip {
    transition: opacity 250ms ease-out;
  }
}
</style>