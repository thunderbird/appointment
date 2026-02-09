<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useI18n } from 'vue-i18n';
import { UserAvatar } from '@thunderbirdops/services-ui';

defineProps<{
  username: string;
  avatarUrl?: string;
}>();

const accountsTbProfileUrl = import.meta.env?.VITE_TB_ACCOUNT_DASHBOARD_URL;
const supportUrl = import.meta.env?.VITE_SUPPORT_URL;

const { t } = useI18n();

const showMenu = ref(false);
const menuRef = ref<HTMLElement | null>(null);

const toggleMenu = () => {
  showMenu.value = !showMenu.value;
};

const handleClickOutside = (event: MouseEvent) => {
  if (menuRef.value && !menuRef.value.contains(event.target as Node)) {
    showMenu.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<template>
  <button class="user-menu" ref="menuRef">
    <user-avatar :username="username" class="avatar" @click="toggleMenu" />

    <div v-if="showMenu" class="dropdown">
      <a :href="accountsTbProfileUrl">
        {{ t('label.account') }}
      </a>
      <a :href="supportUrl">
        {{ t('label.support') }}
      </a>
      <router-link :to="{ name: 'logout' }">
        {{ t('label.logOut') }}
      </router-link>
    </div>
  </button>
</template>

<style scoped>
  .user-menu {
    position: relative;
    display: inline-block;
    background: none;
    border: none;
    cursor: pointer;

    .avatar {
      & :first-child {
        color: var(--colour-ti-base-dark);
      }
    }

    .dropdown {
      position: absolute;
      right: 0;
      margin-top: 0.5rem;
      background: var(--colour-ti-base-light);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 0.5rem;
      box-shadow: 0 0.5rem 1.5rem rgba(0, 0, 0, 0.2);
      padding: 0.5rem 0.25rem;
      min-width: 150px;

      a {
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        color: white;
        text-decoration: none;
        padding: 0.75rem 0.375rem;
        font-family: metropolis;
        font-size: 0.6875rem;
        text-transform: uppercase;
        font-weight: 500;
        border-radius: 0.25rem;

        &:hover {
          background: rgba(255, 255, 255, 0.06);
        }
      }
    }
  }
</style>
