<template>
  <p class="mb-2 text-lg">{{ t('text.googlePermissionDisclaimer') }}</p>
  <ul class="text-md mx-8 list-disc">
    <li>
      <strong>
        {{ t('text.googlePermissionEventsName') }}
      </strong> - {{ t('text.googlePermissionEventReason') }}
    </li>
    <li>
      <strong>
        {{ t('text.googlePermissionCalendarName') }}
      </strong> - {{ t('text.googlePermissionCalendarReason') }}
    </li>
  </ul>
  <i18n-t
    :keypath="`text.settings.connectedAccounts.connect.googleLegal.text`"
    tag="label"
    :for="`text.settings.connectedAccounts.connect.googleLegal.link`"
  >
    <a
      class="underline"
      href="https://developers.google.com/terms/api-services-user-data-policy"
      target="_blank"
    >
      {{ t(`text.settings.connectedAccounts.connect.googleLegal.link`) }}
    </a>
  </i18n-t>
</template>

<script setup>
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

</script>
