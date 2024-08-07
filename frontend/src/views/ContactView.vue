<script setup lang="ts">
import { inject, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useUserStore } from '@/stores/user-store';
import { AlertSchemes } from '@/definitions';
import { callKey } from '@/keys';
import { BooleanResponse } from '@/models';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import AlertBox from '@/elements/AlertBox.vue';
import TextInput from '@/elements/TextInput.vue';

// icons
import { IconSend } from '@tabler/icons-vue';

// component constants
const user = useUserStore();
const { t } = useI18n();
const call = inject(callKey);

// form data
const form = ref<HTMLFormElement>(null);
const topic = ref('');
const details = ref('');
const sendingState = ref(0);

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
  const postObj = { topic: topic.value, details: details.value };
  const { error, data }: BooleanResponse = await call('support').post(postObj).json();
  if (!error.value && data.value) {
    sendingState.value = AlertSchemes.Success;
    resetForm();
  } else {
    sendingState.value = AlertSchemes.Error;
  }
};
</script>

<template>
  <!-- page title area -->
  <div v-if="user.exists()" class="flex flex-col items-center justify-center gap-4">
    <div class="text-4xl font-light">{{ t('heading.contactRequest') }}</div>
    <div class="w-full max-w-lg">{{ t('text.contactRequestForm') }}</div>
    <alert-box
      v-if="sendingState === AlertSchemes.Success"
      :title="t('label.success')"
      @close="sendingState = 0"
      :scheme="AlertSchemes.Success"
    >
      {{ t('info.messageWasSent') }}
    </alert-box>
    <alert-box
      v-if="sendingState === AlertSchemes.Error"
      :title="t('label.error')"
      @close="sendingState = 0"
      :scheme="AlertSchemes.Error"
    >
      {{ t('info.messageWasNotSent') }}
    </alert-box>
    <form class="flex w-full max-w-lg flex-col gap-2" ref="form">
      <label class="flex flex-col gap-1">
        <div class="font-medium text-gray-500 dark:text-gray-300">
          {{ t("label.topic") }}
        </div>
        <input type="text" v-model="topic" class="w-full rounded-md" required />
      </label>
      <label class="flex flex-col gap-1">
        <div class="font-medium text-gray-500 dark:text-gray-300">
          {{ t("label.message") }}
        </div>
        <text-input
          v-model="details"
          :placeholder="t('placeholder.writeHere')"
          :maxlength="2500"
        />
      </label>
    </form>
    <primary-button class="btn-send" @click="send" :title="t('label.send')">
      <icon-send />
      {{ t('label.send') }}
    </primary-button>
  </div>
</template>
