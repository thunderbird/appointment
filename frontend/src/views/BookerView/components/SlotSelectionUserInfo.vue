<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { TextInput } from '@thunderbirdops/services-ui';
import { useBookingViewStore } from '@/stores/booking-view-store';
import { HTMLInputElementEvent } from '@/models';

const { t } = useI18n();
const bookingViewStore = useBookingViewStore();

const { guestUserInfo, guestUserInfoValid } = storeToRefs(bookingViewStore)

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
</script>

<template>
  <div class="user-info-container">
    <text-input required name="booker-view-user-name" v-model="guestUserName">
      {{ t('label.name') }}
    </text-input>

    <text-input required type="email" name="booker-view-user-email" v-model="guestUserEmail" @input="onGuestUserEmailChanged">
      {{ t('label.email') }}
    </text-input>
  </div>
</template>

<style scoped>
.user-info-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  background-color: var(--colour-neutral-raised);
  border-radius: 0.25rem;
}
</style>