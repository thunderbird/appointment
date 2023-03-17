<template>
  <!-- page title area -->
  <div class="flex justify-between items-start select-none">
    <div class="text-4xl font-light">{{ t('heading.yourProfile') }}</div>
  </div>
  <div class="grid grid-cols-2 my-4">
    <template v-for="(value, key) in user" :key="key">
      <pre>{{ key }}</pre>
      <div>{{ value }}</div>
    </template>
  </div>
  <primary-button :label="t('label.logOut')" @click="logout()" />
</template>

<script setup>
import { inject, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import PrimaryButton from '@/elements/PrimaryButton';

// component constants
const auth = inject('auth');

// component constants
const { t } = useI18n();
const refresh = inject('refresh');

// view properties
defineProps({
  calendars:    Array,  // list of calendars from db
  appointments: Array,  // list of appointments from db
  user:         Object, // currently logged in user, null if not logged in
});

// do log out
const logout = () => {
  auth.logout({
    logoutParams: {
      returnTo: window.location.origin
    }
  });
};

// initially load data when component gets remounted
onMounted(async () => {
  await refresh();
});
</script>
