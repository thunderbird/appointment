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
        <icon-search class="absolute top-1/2 -translate-y-1/2 left-4 cursor-text h-4 w-4 stroke-2 stroke-gray-300 fill-transparent" /> 
        <input class="w-full text-sm pl-12 pr-2 rounded-md border-gray-300" type="search" name="search" :placeholder="t('label.search')" />
      </label>
      <!-- menu -->
      <div
        v-for="(view, key) in settingsSections"
        :key="key"
        class="rounded-lg font-semibold text-gray-500 bg-gray-100 p-4 cursor-pointer flex justify-between"
        :class="{ 'bg-teal-500 text-white': view === activeView }"
        @click="show(key)"
      >
        <span>{{ t('label.' + key) }}</span>
        <icon-chevron-right
          class="h-6 w-6 stroke-1 stroke-gray-800 fill-transparent rotate-180 transition-transform"
          :class="{ '!rotate-0 stroke-white': view === activeView }"
        />
      </div>
    </div>
    <!-- content -->
    <div class="w-4/5 pt-14">
      <div v-if="activeView === settingsSections.general" class="flex flex-col gap-8">
        <div class="text-3xl text-gray-500 font-semibold">{{ t('heading.generalSettings') }}</div>
        <div class="pl-6">
          <div class="text-xl">{{ t('heading.languageAndAppearance') }}</div>
          <div class="pl-6 mt-6">
            <div class="text-lg">{{ t('label.language') }}</div>
            <label class="pl-4 mt-4 flex items-center">
              <div class="w-full max-w-2xs">{{ t('label.language') }}</div>
              <select class="w-full max-w-sm rounded-md bg-gray-50 border-gray-200 w-full">
                <option value="en-us">English (US)</option>
                <option value="de-de">German</option>
              </select>
            </label>
          </div>
          <div class="pl-6 mt-6">
            <div class="text-lg">{{ t('label.appearance') }}</div>
            <label class="pl-4 mt-4 flex items-center">
              <div class="w-full max-w-2xs">{{ t('label.theme') }}</div>
              <select class="w-full max-w-sm rounded-md bg-gray-50 border-gray-200 w-full">
                <option value="light">Light</option>
                <option value="dark">Dark</option>
              </select>
            </label>
            <label class="pl-4 mt-4 flex items-center">
              <div class="w-full max-w-2xs">{{ t('label.defaultFont') }}</div>
              <select class="w-full max-w-sm rounded-md bg-gray-50 border-gray-200 w-full">
                <option value="os">Open Sans</option>
                <option value="fs">Fira Sans</option>
              </select>
            </label>
          </div>
        </div>
        <div class="pl-6">
          <div class="text-xl">{{ t('heading.dateAndTimeFormatting') }}</div>
          <div class="pl-6 mt-6 inline-grid grid-cols-2 gap-y-8 gap-x-16">
            <div class="text-lg">{{ t('label.timeFormat') }}</div>
            <div class="text-lg">{{ t('label.dateFormat') }}</div>
            <label class="pl-4 flex gap-4 items-center cursor-pointer">
              <input type="radio" name="timeFormat" class="text-teal-500" />
              <div class="w-full max-w-2xs">{{ t('label.12hAmPm') }}</div>
            </label>
            <label class="pl-4 flex gap-4 items-center cursor-pointer">
              <input type="radio" name="dateFormat" class="text-teal-500" />
              <div class="w-full max-w-2xs">{{ t('label.DDMMYYYY') }}</div>
            </label>
            <label class="pl-4 flex gap-4 items-center cursor-pointer">
              <input type="radio" name="timeFormat" class="text-teal-500" />
              <div class="w-full max-w-2xs">{{ t('label.24h') }}</div>
            </label>
            <label class="pl-4 flex gap-4 items-center cursor-pointer">
              <input type="radio" name="dateFormat" class="text-teal-500" />
              <div class="w-full max-w-2xs">{{ t('label.MMDDYYYY') }}</div>
            </label>
          </div>
          <div class="pl-6 mt-6">
            <div class="text-lg">{{ t('label.timeZone') }}</div>
            <label class="pl-4 mt-4 flex items-center">
              <div class="w-full max-w-2xs">{{ t('label.primaryTimeZone') }}</div>
              <select class="w-full max-w-sm rounded-md bg-gray-50 border-gray-200 w-full">
                <option value="-8">(GMT-8) Pacific Time/Vancouver</option>
              </select>
            </label>
            <label class="pl-4 mt-6 flex items-center">
              <div class="w-full max-w-2xs">{{ t('label.showSecondaryTimeZone') }}</div>
              <switch-toggle :active="false" />
            </label>
            <label class="pl-4 mt-6 flex items-center">
              <div class="w-full max-w-2xs">{{ t('label.secondaryTimeZone') }}</div>
              <select class="w-full max-w-sm rounded-md bg-gray-50 border-gray-200 w-full">
                <option value="-8">(GMT-8) Pacific Time/Vancouver</option>
              </select>
            </label>
          </div>
        </div>
      </div>
      <div v-if="activeView === settingsSections.calendar">
        <div class="text-3xl text-gray-500 font-semibold">{{ t('heading.calendarSettings') }}</div>
      </div>
      <div v-if="activeView === settingsSections.appointmentsAndBooking">
        <div class="text-3xl text-gray-500 font-semibold">{{ t('heading.appointmentsAndBookingSettings') }}</div>
      </div>
      <div v-if="activeView === settingsSections.account">
        <div class="text-3xl text-gray-500 font-semibold">{{ t('heading.accountSettings') }}</div>
      </div>
      <div v-if="activeView === settingsSections.privacy">
        <div class="text-3xl text-gray-500 font-semibold">{{ t('heading.privacySettings') }}</div>
      </div>
      <div v-if="activeView === settingsSections.faq">
        <div class="text-3xl text-gray-500 font-semibold">{{ t('heading.frequentlyAskedQuestions') }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { settingsSections } from '@/definitions';
import SwitchToggle from '@/elements/SwitchToggle.vue';
import IconSearch from '@/elements/icons/IconSearch.vue';
import IconChevronRight from '@/elements/icons/IconChevronRight.vue';
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from 'vue-router';
const { t } = useI18n();
const route = useRoute();
const router = useRouter();

// menu navigation of different views
const activeView = ref(route.params.view ? settingsSections[route.params.view] : settingsSections.general);
const show = (key) => {
  router.replace({ name: route.name, params: { view: key } });
  activeView.value = settingsSections[key];
};
</script>
