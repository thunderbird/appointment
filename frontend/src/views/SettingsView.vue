<template>
  <!-- page title area -->
  <div class="flex justify-between items-start select-none">
    <div class="text-4xl font-light">{{ t('label.settings') }}</div>
  </div>
  <div class="flex justify-between gap-24 mt-8 pb-16 items-stretch">
    <!-- sidebar navigation -->
    <div class="w-1/5 flex flex-col gap-6">
      <!-- search -->
      <label class="flex items-center relative">
        <icon-search
          class="
            absolute top-1/2 -translate-y-1/2 left-4 cursor-text h-4 w-4 stroke-2
            stroke-gray-300 dark:stroke-gray-500 fill-transparent
          "
        /> 
        <input
          class="w-full text-sm pl-12 pr-2 rounded-md"
          type="search"
          name="search"
          :placeholder="t('label.search')"
        />
      </label>
      <!-- menu -->
      <div
        v-for="(view, key) in settingsSections"
        :key="key"
        class="
          rounded-lg font-semibold p-4 cursor-pointer flex justify-between
          text-gray-500 dark:text-gray-300 bg-gray-100 dark:bg-gray-600
        "
        :class="{ '!bg-teal-500 !text-white': view === activeView }"
        @click="show(key)"
      >
        <span>{{ t('label.' + key) }}</span>
        <icon-chevron-right
          class="
            h-6 w-6 stroke-1 fill-transparent rotate-180 transition-transform
            stroke-gray-800 dark:stroke-gray-300
          "
          :class="{ '!rotate-0 !stroke-white': view === activeView }"
        />
      </div>
    </div>
    <!-- content -->
    <div class="w-4/5 pt-14">

      <!-- general settings -->
      <settings-general v-if="activeView === settingsSections.general" :user="user" />
      
      <!-- calendar settings -->
      <settings-calendar v-if="activeView === settingsSections.calendar" :calendars="calendars" />

      <!-- appointments and booking settings -->
      <div v-if="activeView === settingsSections.appointmentsAndBooking">
        <div class="text-3xl text-gray-500 font-semibold">{{ t('heading.appointmentsAndBookingSettings') }}</div>
      </div>

      <!-- account settings -->
      <div v-if="activeView === settingsSections.account">
        <div class="text-3xl text-gray-500 font-semibold">{{ t('heading.accountSettings') }}</div>
      </div>

      <!-- privacy settings -->
      <div v-if="activeView === settingsSections.privacy">
        <div class="text-3xl text-gray-500 font-semibold">{{ t('heading.privacySettings') }}</div>
      </div>

      <!-- faq settings -->
      <div v-if="activeView === settingsSections.faq">
        <div class="text-3xl text-gray-500 font-semibold">{{ t('heading.frequentlyAskedQuestions') }}</div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { settingsSections } from '@/definitions';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import SettingsGeneral from '@/components/SettingsGeneral';
import SettingsCalendar from '@/components/SettingsCalendar';

// icons
import {
  IconChevronRight,
  IconSearch,
} from '@tabler/icons-vue';

// component constants
const { t } = useI18n({ useScope: 'global' });
const route = useRoute();
const router = useRouter();

// view properties
defineProps({
  calendars:    Array,  // list of calendars from db
  appointments: Array,  // list of appointments from db
  user:         Object, // currently logged in user, null if not logged in
});

// menu navigation of different views
const activeView = ref(route.params.view ? settingsSections[route.params.view] : settingsSections.general);
const show = (key) => {
  router.replace({ name: route.name, params: { view: key } });
  activeView.value = settingsSections[key];
};
</script>
