<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { PrimaryButton, TextInput } from '@thunderbirdops/services-ui';
import { useUserStore } from '@/stores/user-store';
import { useBookingViewStore } from '@/stores/booking-view-store';
import { HTMLInputElementEvent } from '@/models';
import { AlertSchemes } from '@/definitions';
import AlertBox from '@/elements/AlertBox.vue';

enum Tab {
  GUEST,
  SIGN_IN
}

const { t } = useI18n();
const userStore = useUserStore();
const bookingViewStore = useBookingViewStore();
const userLoginFormRef = useTemplateRef('user-login-form');

const { guestUserInfo, guestUserInfoValid } = storeToRefs(bookingViewStore)

const selectedTab = ref<Tab>(Tab.GUEST);
const userLoginEmail = ref('');
const userLoginPassword = ref('');
const userLoginError = ref('');
const userLoginLoading = ref(false);

const guestUserName = computed({
  get: () => guestUserInfo.value.name,
  set: (value) => {
    bookingViewStore.$patch({ guestUserInfo: { name: value } })
  }
})

const guestUserEmail = computed({
  get: () => guestUserInfo.value.email,
  set: (value) => {
    bookingViewStore.$patch({ guestUserInfo: { email: value } })
  }
})

const onGuestUserEmailChanged = (e: HTMLInputElementEvent) => {
  guestUserInfoValid.value = e.target.checkValidity();
}

const onLogin = async () => {
  userLoginError.value = '';
  userLoginLoading.value = true;

  if (userLoginFormRef.value.checkValidity()) {
    const { error } = await userStore.login(userLoginEmail.value, userLoginPassword.value);

    if (error) {
      // FIXME: The return of the login function is not standardized at the moment
      // and currently inferred as string | boolean but it does return an object
      // with a detail key in this case
      userLoginError.value = (error as any)?.detail;
      userLoginLoading.value = false;
      return;
    }
  }

  userLoginLoading.value = false;
}
</script>

<template>
  <div class="user-info-container">
    <div class="user-info-tabs">
      <button
        :class="{ 'selected': selectedTab === Tab.GUEST }"
        @click="selectedTab = Tab.GUEST"
      >
        {{ t('label.continueAsGuest') }}
      </button>
      <button
        :class="{ 'selected': selectedTab === Tab.SIGN_IN }"
        @click="selectedTab = Tab.SIGN_IN"
      >
        {{ t('label.signIn') }}
      </button>
    </div>

    <template v-if="selectedTab === Tab.GUEST">
      <text-input name="booker-view-user-name" v-model="guestUserName">
        {{ t('label.name') }}
      </text-input>

      <text-input required type="email" name="booker-view-user-email" v-model="guestUserEmail" @input="onGuestUserEmailChanged">
        {{ t('label.email') }}
      </text-input>
    </template>
  
    <template v-else-if="selectedTab === Tab.SIGN_IN">
      <form ref="user-login-form" @submit.prevent @keyup.enter="onLogin">
        <text-input required type="email" name="booker-view-user-email" v-model="userLoginEmail">
          {{ t('label.email') }}
        </text-input>
  
        <text-input type="password" required name="booker-view-user-password" v-model="userLoginPassword">
          {{ t('label.password') }}
        </text-input>
  
        <alert-box
          v-if="userLoginError"
          :alert="{ title: userLoginError }"
          :scheme="AlertSchemes.Error"
          @close="userLoginError = ''"
        />

        <primary-button class="sign-in-button" @click="onLogin" :disabled="userLoginLoading">
          {{ t('label.signIn') }}
        </primary-button>
      </form>
    </template>
  </div>
</template>

<style scoped>
.user-info-container {
  padding: 1rem 0.5rem;
  background-color: var(--colour-neutral-raised);
  border-radius: 0.25rem;

  .user-info-tabs {
    display: flex;
    justify-content: end;
    margin-block-end: 1rem;

    button {
      padding-inline: 1rem;
      color: var(--colour-ti-muted);
      border-block-end: 1px solid var(--colour-neutral-border);

      &.selected {
        color: var(--colour-ti-base);
        border-block-end: 1px solid var(--colour-neutral-border-intense);
      }
    }
  }

  form {
    display: flex;
    gap: 1rem;
    flex-grow: 1;
    flex-direction: column;
  }

  .sign-in-button {
    align-self: end;
  }
}
</style>