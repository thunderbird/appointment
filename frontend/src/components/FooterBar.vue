<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import { useUserStore } from '@/stores/user-store';

const { t } = useI18n();
const userStore = useUserStore();

const { authenticated: isAuthenticated } = storeToRefs(userStore);

const appointmentNotLoggedInNavItems = [
  { route: 'login', i18nKey: 'logIn' },
  { route: 'waiting-list', i18nKey: 'signUpForBeta' },
];

const appointmentLoggedInNavItems = [
  { route: 'dashboard', i18nKey: 'dashboard' },
  { route: 'bookings', i18nKey: 'bookings' },
  { route: 'availability', i18nKey: 'availability' },
  { route: 'settings', i18nKey: 'settings' },
];

const mozillaNavItems = [
  { 
    i18nKey: 'privacyPolicy', 
    type: 'internal', 
    route: 'privacy' 
  },
  { 
    i18nKey: 'cookies', 
    type: 'external', 
    urlKey: 'cookies'
  },
  { 
    i18nKey: 'legal', 
    type: 'internal', 
    route: 'terms' 
  },
  { 
    i18nKey: 'sendDMCANotice', 
    type: 'external', 
    urlKey: 'dmcaNotice'
  },
  { 
    i18nKey: 'reportFraud', 
    type: 'external', 
    urlKey: 'reportFraud'
  },
  { 
    i18nKey: 'participationGuidelines', 
    type: 'external', 
    urlKey: 'participationGuidelines'
  },
];

const urlMap = {
  cookies: 'https://www.mozilla.org/privacy/websites/#data-tools',
  dmcaNotice: 'https://www.mozilla.org/en-US/about/legal/report-infringement/',
  reportFraud: 'https://www.mozilla.org/about/legal/fraud-report/',
  participationGuidelines: 'https://www.mozilla.org/en-US/about/governance/policies/participation/',
  mzlaLink: 'https://blog.thunderbird.net/2020/01/thunderbirds-new-home/',
  creativeCommonsLink: 'https://www.mozilla.org/en-US/foundation/licensing/website-content/',
  contributeToThisSite: 'https://github.com/thunderbird/appointment',
} as const;

const getUrl = (key: keyof typeof urlMap): string => urlMap[key];
</script>

<template>
  <footer>
    <nav class="appointment-navigation">
      <img src="@/assets/svg/appointment_logo.svg" alt="Appointment Logo" />
      <ul v-if="isAuthenticated">
        <li v-for="navItem in appointmentLoggedInNavItems" :key="navItem.route">
          <router-link :to="navItem.route">  
            {{ t(`label.${navItem.i18nKey}`) }}
          </router-link>
        </li>
      </ul>

      <ul v-else>
        <li v-for="navItem in appointmentNotLoggedInNavItems" :key="navItem.route">
          <router-link :to="navItem.route">  
            {{ t(`label.${navItem.i18nKey}`) }}
          </router-link>
        </li>
      </ul>
    </nav>

    <hr />

    <div class="mozilla-navigation">
      <img src="@/assets/svg/mozilla-logo.svg" alt="Mozilla Logo" />
      <div class="mozilla-navigation-content">
        <ul>
          <li v-for="navItem in mozillaNavItems" :key="navItem.i18nKey">
            <router-link 
              v-if="navItem.type === 'internal'" 
              :to="{ name: navItem.route }" 
              target="_blank"
            >
              {{ t(`label.${navItem.i18nKey}`) }}
            </router-link>

            <a 
              v-else 
              :href="getUrl((navItem).urlKey as keyof typeof urlMap)" 
              target="_blank"
            >
              {{ t(`label.${navItem.i18nKey}`) }}
            </a>
          </li>
        </ul>

        <p>
          <i18n-t keypath="text.homepage.copywrite" scope="global">
            <template v-slot:mzlaLink>
              <a :href="getUrl('mzlaLink')">
                {{ $t('text.homepage.mzlaLinkText') }}
              </a>
            </template>
            <template v-slot:currentYear>
              {{ new Date().getFullYear() }}
            </template>
            <template v-slot:creativeCommonsLink>
              <a :href="getUrl('creativeCommonsLink')">
                {{ $t('text.homepage.creativeCommonsLinkText') }}
              </a>
            </template>
          </i18n-t>
        </p>

        <a class="underline" :href="getUrl('contributeToThisSite')" target="_blank">
          {{ t('label.contributeToThisSite' )}}
        </a>
      </div>
    </div>
  </footer>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

footer {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 2rem 1rem;
  background-image: linear-gradient(138deg, #1b2128 34%, #171b24 55%);

  .underline, a:hover {
    text-decoration: underline;
  }

  .appointment-navigation {
    display: flex;
    flex-direction: column;
    align-items: start;
    justify-content: space-between;

    img {
      align-self: center;
      margin-block-end: 2rem;
    }

    ul {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      font-family: metropolis;
      font-weight: 600;
      font-size: 0.8125rem;
      text-transform: uppercase;

      /* FIXME: This should be a var but we don't have a background
      for the footer in light mode yet so it is not readable if not white-ish */
      color: white;
    }
  }

  .mozilla-navigation {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    font-family: Inter;
    font-size: 0.75rem;

    img {
      height: 36px;
    }

    ul {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .mozilla-navigation-content {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;

      /* FIXME: This should be --colour-ti-base but we don't have a background
      for the footer in light mode yet so it is not readable if we use the var */
      color: #EEEEF0;
    }
  }
}

@media (--md) {
  footer {
    gap: 2.5rem;
    padding: 3rem 3.5rem 5rem;

    .appointment-navigation {
      flex-direction: row;
      align-items: center;

      img {
        margin-block-end: 0;
      }

      ul {
        flex-direction: row;
        gap: 3rem;
      }
    }

    .mozilla-navigation {
      flex-direction: row;
      gap: 6rem;

      ul {
        flex-direction: row;
        gap: 2.25rem;
      }
    }
  }
}
</style>
