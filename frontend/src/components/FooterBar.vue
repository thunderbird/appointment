<script setup lang="ts">
import { inject } from 'vue';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import { useUserStore } from '@/stores/user-store';
import { StandardFooter } from '@thunderbirdops/services-ui';
import { supportUrlKey, tbProUrlKey } from '@/keys';
import { STATUS_PAGE_URL, IDEAS_PAGE_URL } from '@/definitions';

const tbProUrl = inject(tbProUrlKey);
const supportUrl = inject(supportUrlKey);

const { t } = useI18n();
const userStore = useUserStore();

const { authenticated: isAuthenticated } = storeToRefs(userStore);

const appointmentNotLoggedInNavItems = [{ route: tbProUrl, i18nKey: 'exploreThundermail', external: true }];

const appointmentLoggedInNavItems = [
  { route: 'dashboard', i18nKey: 'calendar' },
  { route: 'bookings', i18nKey: 'bookings' },
  { route: 'availability', i18nKey: 'availability' },
  { route: 'settings', i18nKey: 'settings' },
];
</script>

<template>
  <StandardFooter contributeToThisSiteUrl="https://github.com/thunderbird/appointment">
    <template #default>
      <nav class="appointment-navigation">
        <div class="top-row">
          <img src="@/assets/svg/thunderbird-logo.svg" alt="Thunderbird Logo" />

          <ul v-if="isAuthenticated">
            <li v-for="navItem in appointmentLoggedInNavItems" :key="navItem.route">
              <router-link :to="navItem.route">
                {{ t(`label.${navItem.i18nKey}`) }}
              </router-link>
            </li>
          </ul>

          <ul v-else>
            <li v-for="navItem in appointmentNotLoggedInNavItems" :key="navItem.route">
              <a v-if="navItem.external" :href="navItem.route">
                {{ t(`label.${navItem.i18nKey}`) }}
              </a>

              <router-link v-else :to="navItem.route">
                {{ t(`label.${navItem.i18nKey}`) }}
              </router-link>
            </li>
          </ul>
        </div>

        <ul v-if="isAuthenticated" class="default-links">
          <a :href="STATUS_PAGE_URL" target="_blank" rel="noopener noreferrer">
            {{ t('label.status') }}
          </a>
          <span>|</span>
          <a :href="supportUrl" target="_blank" rel="noopener noreferrer">
            {{ t('label.needHelpVisitSupport') }}
          </a>
          <span>|</span>
          <a :href="IDEAS_PAGE_URL" target="_blank" rel="noopener noreferrer">
            {{ t('label.ideas') }}
          </a>
        </ul>
      </nav>
    </template>

    <template #privacyPolicy>
      <router-link to="/privacy">
        {{ t('label.privacyPolicy') }}
      </router-link>
    </template>

    <template #legal>
      <router-link to="/terms">
        {{ t('label.legal') }}
      </router-link>
    </template>
  </StandardFooter>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.appointment-navigation {
  display: flex;
  flex-direction: column;
  align-items: start;
  gap: 1.75rem;

  .top-row {
    display: flex;
    flex-direction: column;
    align-items: start;
    width: 100%;

    img {
      margin-block-end: 2rem;
    }
  }

  ul {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    font-family: metropolis;
    font-weight: 600;
    font-size: 0.8125rem;
    text-transform: uppercase;

    /* FIXME: This should be a var but we don't have a background
    for the footer in light mode yet so it is not readable if not white-ish */
    color: white;
  }

  .default-links {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    font-family: Inter, sans-serif;
    font-weight: 400;
    font-size: 0.6875rem;
    text-transform: none;
    color: var(--colour-ti-secondary-dark);

    a {
      text-decoration: underline;
      color: inherit;
    }
  }
}

@media (--md) {
  .appointment-navigation {
    gap: 0.75rem;

    .top-row {
      flex-direction: row;
      align-items: center;
      justify-content: space-between;
      height: 61px;

      img {
        margin-block-end: 0;
      }
    }

    .default-links {
      width: 100%;
      justify-content: flex-end;
    }

    ul {
      gap: 3rem;
    }
  }
}
</style>
