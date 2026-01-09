<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import { useUserStore } from '@/stores/user-store';
import { StandardFooter } from '@thunderbirdops/services-ui';

const tbProUrl = import.meta.env.VITE_TB_PRO_URL;
const supportUrl = import.meta.env?.VITE_SUPPORT_URL;

const { t } = useI18n();
const userStore = useUserStore();

const { authenticated: isAuthenticated } = storeToRefs(userStore);

const appointmentNotLoggedInNavItems = [
  { route: tbProUrl, i18nKey: 'exploreThunderbirdPro', external: true },
];

const appointmentLoggedInNavItems = [
  { route: 'dashboard', i18nKey: 'dashboard' },
  { route: 'bookings', i18nKey: 'bookings' },
  { route: 'availability', i18nKey: 'availability' },
  { route: 'settings', i18nKey: 'settings' },
];
</script>

<template>
  <StandardFooter
    contributeToThisSiteUrl="https://github.com/thunderbird/appointment"
  >
    <template #default>
      <nav class="appointment-navigation">
        <img src="@/assets/svg/appointment_logo.svg" alt="Appointment Logo" />
        <div>
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
          <a :href="supportUrl" class="contact-support-link">
            {{ t('label.needHelpVisitSupport') }}
          </a>
        </div>
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
  justify-content: space-between;

  img {
    align-self: start;
    margin-block-end: 2rem;
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

  .contact-support-link {
    display: block;
    font-family: Inter, sans-serif;
    font-size: 0.6875rem;
    font-weight: normal;
    text-decoration: underline;
    margin-block-start: 1.5rem;

    /* FIXME: This should be a var but we don't have a background
    for the footer in light mode yet so it is not readable if not white-ish */
    color: white;
  }
}

@media (--md) {
  .appointment-navigation {
    flex-direction: row;
    align-items: center;

    img {
      margin-block-end: 0;
    }

    ul {
      gap: 3rem;
    }

    .contact-support-link {
      text-align: end;
    }
  }
}
</style>
