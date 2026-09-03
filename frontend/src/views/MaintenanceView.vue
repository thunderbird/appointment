<script setup lang="ts">
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
</script>

<template>
  <div class="page-contents">
    <img class="logo-light" src="@/assets/svg/appointment_calendar_logo_monochrome_light.svg" alt="" />
    <img class="logo-dark" src="@/assets/svg/appointment_calendar_logo_monochrome_dark.svg" alt="" />
    <h2>{{ t('maintenance.title') }}</h2>
    <p class="subline">{{ t('maintenance.unavailable') }}<br />{{ t('maintenance.checkBackSoon') }}</p>
    <i18n-t keypath="maintenance.moreInformation" tag="p" scope="global" class="more-information">
      <template v-slot:statusPage>
        <a href="https://status.tb.pro" target="_blank">{{ t('maintenance.statusPage') }}</a>
      </template>
      <template v-slot:lineBreak><br /></template>
      <template v-slot:supportKnowledgeBase>
        <a href="https://support.tb.pro/hc/categories/43160497669011" target="_blank">
          {{ t('maintenance.supportKnowledgeBase') }}
        </a>
      </template>
    </i18n-t>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.page-contents {
  text-align: center;

  img {
    display: inline-block;

    &.logo-light {
      display: none;
    }

    .dark &.logo-dark {
      display: none;
    }
    .dark &.logo-light {
      display: inline-block;
    }
  }

  h2 {
    font-family: Metropolis;
    font-weight: 300;
    font-size: 2rem;
    line-height: 1.2;
    text-align: center;
    margin: 1.5rem 0;
    color: var(--colour-ti-base);
  }

  p {
    color: var(--colour-ti-secondary);
    margin-bottom: 1em;

    a {
      color: var(--colour-primary-pressed);
      text-decoration: underline;
      text-underline-offset: 3px;

      @media (prefers-color-scheme: dark) {
        color: var(--colour-primary-hover);
      }
    }
  }

  .subline {
    line-height: 132%;
  }

  .more-information {
    font-size: 0.875rem;
    line-height: 1.23;
  }

  @media (--md) {
    padding: 0 3.75rem 2rem;
  }
}
</style>
