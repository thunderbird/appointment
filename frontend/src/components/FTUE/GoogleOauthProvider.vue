<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { onMounted, inject, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useRoute, useRouter } from 'vue-router';
import SecondaryButton from '@/tbpro/elements/SecondaryButton.vue';
import { useFTUEStore } from '@/stores/ftue-store';
import { createCalendarStore } from '@/stores/calendar-store';
import { useUserStore } from '@/stores/user-store';
import { createExternalConnectionsStore } from '@/stores/external-connections-store';
import { callKey } from '@/keys';
import { ExternalConnectionProviders } from '@/definitions';
import {
  BooleanResponse, Exception, ExceptionDetail,
} from '@/models';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const call = inject(callKey);
// component properties
interface Props {
  showPrevious?: boolean,
  showSwitch?: boolean,
}
withDefaults(defineProps<Props>(), {
  showPrevious: false,
  showSwitch: false,
});
const emits = defineEmits(['next', 'previous', 'switch']);

const isLoading = ref(false);

const ftueStore = useFTUEStore();
const { hasNextStep, errorMessage } = storeToRefs(ftueStore);

const calendarStore = createCalendarStore(call);
const externalConnectionStore = createExternalConnectionsStore(call);
const { calendars } = storeToRefs(calendarStore);
const initFlowKey = 'tba/startedCalConnect';

onMounted(async () => {
  await calendarStore.fetch(true);
  const hasFlowKey = localStorage?.getItem(initFlowKey);
  const noCalendarsError = hasFlowKey && calendars.value.length === 0;

  // Error occurred during flow
  if (route.query.error || noCalendarsError) {
    localStorage?.removeItem(initFlowKey);
    if (noCalendarsError) {
      errorMessage.value = {
        title: t('error.externalAccountHasNoCalendars', { external: 'Google' }),
        details: null,
      };

      // Also remove the google calendar
      if (externalConnectionStore.google.length > 0) {
        await externalConnectionStore.disconnect(ExternalConnectionProviders.Google);
      }
    } else {
      errorMessage.value = {
        title: route.query.error as string,
        details: null,
      };
    }
    await router.replace(route.path);
  }

  if (localStorage?.getItem(initFlowKey)) {
    localStorage?.removeItem(initFlowKey);

    const { data, error }: BooleanResponse = await call('google/ftue-status').get().json();
    // Did they hit back?
    if (error?.value) {
      errorMessage.value = {
        title: ((data.value as Exception)?.detail as ExceptionDetail)?.message,
        details: null,
      };
      return;
    }

    emits('next');
  }
});

const onSubmit = async () => {
  const user = useUserStore();

  isLoading.value = true;

  // Create key so we can move to the next page after we come back
  localStorage?.setItem(initFlowKey, 'true');
  await calendarStore.connectGoogleCalendar(user.data.email);
};

</script>

<template>
  <div class="content">
    <div class="card">
      <p class="">{{ t('text.googlePermissionDisclaimer') }}</p>
      <ul class="">
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
    </div>
  </div>
  <div class="buttons">
    <secondary-button
      class="btn-switch"
      @click="emits('switch')"
      v-if="showSwitch">
        {{ t('calDAVForm.switchToCalDAV') }}
    </secondary-button>
    <secondary-button
      class="btn-back"
      :title="t('label.back')"
      v-if="showPrevious"
      :disabled="isLoading"
      @click="emits('previous')"
    >{{ t('label.back') }}
    </secondary-button>
    <secondary-button
      class="btn-continue"
      :title="t('label.connectGoogleCalendar')"
      v-if="hasNextStep"
      @click="onSubmit()"
      :disabled="isLoading"
    >
      <template v-slot:icon><span :title="t('ftue.googleCalendarLogo')" class="google-calendar-logo"/></template>
      {{ t('label.connectGoogleCalendar') }}
    </secondary-button>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';
@import '@/assets/styles/mixins.pcss';

.content {
  display: flex;
  margin: auto;
  width: 100%;
}

.card {
  --colour-background: var(--colour-neutral-base);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  padding: 1rem;
  border-radius: 0.5625rem;
  @mixin faded-background var(--colour-background);
  @mixin faded-border var(--colour-background);
  font-size: 0.8125rem;
  margin: auto;
}

.dark {
  .card {
    --colour-background: var(--colour-neutral-lower);
  }
}

.google-calendar-logo {
  display: inline-block;
  background-image: url('@/assets/svg/google-calendar-logo.svg');
  width: 1.625rem;
  height: 1.625rem;
}

.btn-switch {
  margin-left: 0;
  margin-right: auto;
}

.buttons {
  display: flex;
  width: 100%;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
  right: auto;
  left: auto;
}

@media (--md) {
  .card {
    width: 70%;
  }

  .buttons {
    justify-content: flex-end;
    position: absolute;
    bottom: 5.75rem;
    margin: 0;
  }
}
</style>
