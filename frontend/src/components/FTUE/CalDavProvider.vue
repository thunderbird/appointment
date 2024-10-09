<script setup lang="ts">
import { useI18n } from 'vue-i18n';

import SecondaryButton from '@/tbpro/elements/SecondaryButton.vue';
import {
  inject, onMounted, reactive, ref,
} from 'vue';
import { callKey } from '@/keys';
import { useFTUEStore } from '@/stores/ftue-store';
import { storeToRefs } from 'pinia';
import { IconArrowRight } from '@tabler/icons-vue';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import TextInput from '@/tbpro/elements/TextInput.vue';
import { CalendarListResponse } from '@/models';

const ftueStore = useFTUEStore();
const {
  hasNextStep, hasPreviousStep, errorMessage,
} = storeToRefs(ftueStore);
const { previousStep, nextStep } = ftueStore;
const { t } = useI18n();
const call = inject(callKey);
const isLoading = ref(false);
const principal = ref({
  url: '',
  user: '',
  password: '',
});

onMounted(async () => {
  const { data } = await call('/caldav/dns').json();
  principal.value.url = data.value.url;
});

const onSubmit = async () => {
  isLoading.value = true;
  const { error, data }: CalendarListResponse = await call('/caldav/auth').post(principal).json();
  console.log(data.value);
  isLoading.value = false;
  if (!error.value) {
    await nextStep(call);
  }
};
</script>
<template>
  <div class="content">
      <div class="form">
        <text-input name="principal" help="The URL we will use to connect to your calendars." v-model="principal.url">
          Principal URL
        </text-input>
        <text-input name="username" v-model="principal.user">
          Username
        </text-input>
        <text-input type="password" name="password" help="This is usually not your email address password, but an 'App Password'." v-model="principal.password">
          Password
        </text-input>
      </div>
      <div class="buttons">
        <primary-button
          :label="'Search for calendars'"
          :waiting="isLoading"
          @click="onSubmit"
        >{{ t('label.search') }}</primary-button>
      </div>
    </div>
</template>
<style scoped>
@import '@/assets/styles/custom-media.pcss';
@import '@/assets/styles/mixins.pcss';

.content {
  display: flex;
  margin: auto;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.buttons {
  display: flex;
  width: 100%;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}
@media (--md) {
  .buttons {
    justify-content: flex-end;
    position: absolute;
    bottom: 5.75rem;
    margin: 0;
  }
}
</style>
