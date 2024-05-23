<template>
  <div class="mb-4 flex h-12 justify-center gap-8">
    <nav-bar-item
      v-for="item in navItems"
      :key="item"
      :active="route.name == item"
      :label="t(`label.${item}`)"
      :link-name="item"
    />
  </div>
</template>

<script setup>

import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import NavBarItem from '@/elements/NavBarItem.vue';

const { t } = useI18n();

const navItems = [
  'admin-invite-codes-panel',
  'admin-subscriber-panel',
];

const route = useRoute();
</script>
