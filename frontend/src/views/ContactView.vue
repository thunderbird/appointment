<template>
  <!-- page title area -->
  <div v-if="user.exists()" class="flex flex-col gap-4 justify-center items-center">
    <div class="text-4xl font-light">{{ t('heading.contactRequest') }}</div>
    <div class="w-full max-w-lg">{{ t('text.contactRequestForm') }}</div>
    <alert-box
      v-if="sendingState === alertSchemes.succes"
      :title="t('label.success')"
      @close="sendingState = 0"
      :scheme="alertSchemes.succes"
    >
      {{ t('info.messageWasSent') }}
    </alert-box>
    <alert-box
      v-if="sendingState === alertSchemes.error"
      :title="t('label.error')"
      @close="sendingState = 0"
      :scheme="alertSchemes.error"
    >
      {{ t('info.messageWasNotSent') }}
    </alert-box>
    <form class="flex flex-col gap-2 w-full max-w-lg" ref="form">
      <label class="flex flex-col gap-1">
        <div class="font-medium text-gray-500 dark:text-gray-300">
          {{ t("label.topic") }}
        </div>
        <input type="text" v-model="topic" class="rounded-md w-full" required />
      </label>
      <label class="relative flex flex-col gap-1">
        <div class="font-medium text-gray-500 dark:text-gray-300">
          {{ t("label.message") }}
        </div>
        <textarea
          v-model="details"
          :placeholder="t('placeholder.writeHere')"
          class="rounded-md w-full text-sm h-40 place-holder"
          :maxlength="charLimit"
          required
        ></textarea>
        <div
          class="absolute bottom-3 right-3 text-xs"
          :class="{
            'text-orange-500': charCount >= charLimit * 0.92,
            '!text-rose-600': charCount === charLimit,
          }"
        >
          {{ charCount }}/{{ charLimit }}
        </div>
      </label>
    </form>
    <primary-button @click="send">
      <icon-send />
      {{ t('label.send') }}
    </primary-button>
  </div>
</template>

<script setup>
import { inject, ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useUserStore } from '@/stores/user-store';
import { alertSchemes } from '@/definitions';
import PrimaryButton from '@/elements/PrimaryButton';
import AlertBox from '@/elements/AlertBox.vue';

// icons
import { IconSend } from '@tabler/icons-vue';

// component constants
const user = useUserStore();
const { t } = useI18n();
const call = inject('call');

// form data
const form = ref(null);
const topic = ref('');
const details = ref('');
const sendingState = ref(0);

// handle notes char limit
const charLimit = 2500;
const charCount = computed(() => details.value.length);

// empty all form inputs
const resetForm = () => {
  topic.value = '';
  details.value = '';
};

// send support request
const send = async () => {
  if (!form.value.checkValidity()) {
    form.value.reportValidity();
    return;
  }
  const { error, data } = await call('support').post({ topic: topic.value, details: details.value }).json();
  if (!error.value && data.value) {
    sendingState.value = alertSchemes.succes;
    resetForm();
  } else {
    sendingState.value = alertSchemes.error;
  }
};
</script>
