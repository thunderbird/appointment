<script setup lang="ts">
import PrimaryButton from '@/elements/PrimaryButton.vue';
import InfoBox from '@/elements/home/InfoBox.vue';
import HomeFooter from '@/components/HomeFooter.vue';
import { useUserStore } from '@/stores/user-store';
import { useRouter } from 'vue-router';

const router = useRouter();

const isAuthenticated = useUserStore().exists();

const enter = () => {
  router.push('/calendar');
};
const login = () => {
  router.push('/login');
};
</script>

<template>
  <div>
    <section>
      <div class="flex-center mt-8 flex-col gap-12">
        <img class="w-full max-w-xs md:max-w-sm lg:max-w-md" src="/appointment_logo.svg" alt="Appointment Logo" />
        <h2 class="pt-6 text-center font-display text-lg uppercase tracking-[0.19em] md:text-3xl lg:text-5xl">
          {{ $t('app.title') }}
        </h2>
        <div class="flex-center -mb-12 flex flex-col md:-mb-20 lg:-mb-28 xl:-mb-40">
          <h4 class="max-w-2xl pt-12 text-center text-xl font-light leading-9 tracking-wide">
            {{ $t('text.homepage.intro') }}
          </h4>
          <div class="mt-16">
            <primary-button
              v-if="!isAuthenticated"
              :label="$t('label.logIn')"
              class="btn-login"
              @click="login"
              :title="$t('label.logIn')"
            />
            <primary-button
              v-else-if="isAuthenticated"
              :label="$t('label.continue')"
              class="btn-continue"
              @click="enter"
              :title="$t('label.continue')"
            />
          </div>
        </div>
        <div class="w-full">
          <!-- Padding top is rounded up aspect ratio percentage (height / width) of image -->
          <div class="h-0 w-full bg-[url(@/assets/svg/homepage-split.svg)] bg-contain bg-no-repeat pt-[14%] dark:bg-[url(@/assets/svg/homepage-split-dark.svg)]"></div>
        </div>
      </div>
    </section>
    <section class="mx-4">
      <h2 class="py-16 text-center text-3xl text-teal-600 dark:text-teal-400">
        {{ $t('text.homepage.sectionHeader') }}
      </h2>
      <section class="mx-auto flex max-w-full flex-col justify-center gap-16 md:max-w-7xl md:flex-row">
        <info-box :title="$t('text.homepage.planEventTitle')">
          {{ $t('text.homepage.planEventBody') }}
        </info-box>
        <info-box :title="$t('text.homepage.setAvailabilityTitle')">
          {{ $t('text.homepage.setAvailabilityBody') }}
        </info-box>
        <info-box :title="$t('text.homepage.shareWithOthersTitle')">
          {{ $t('text.homepage.shareWithOthersBody') }}
        </info-box>
      </section>
    </section>
    <section class="w-full">
        <div class="w-full bg-[url(@/assets/svg/homepage-wave.svg)] bg-cover bg-top bg-no-repeat dark:bg-[url(@/assets/svg/homepage-wave-dark.svg)]">
          <div class="pt-[13%]"></div>
          <div class="relative mx-auto flex w-full flex-col justify-between md:flex-row">
            <img
              class="my-auto size-full shadow-2xl dark:hidden md:w-1/2"
              src="@/assets/img/homepage-screenshot.png"
              :alt="$t('text.homepage.screenshotCalendarAlt')"
            />
            <img
              class="my-auto hidden size-full shadow-2xl dark:block md:w-1/2"
              src="@/assets/img/homepage-screenshot-dark.png"
              :alt="$t('text.homepage.screenshotCalendarAlt')"
            />
            <div class="flex-center my-20 flex-col md:w-[45%]">
              <p class="w-[70%] text-2xl font-light leading-loose tracking-wide">
                {{ $t('text.homepage.calendarCopy') }}
              </p>
            </div>
          </div>
        </div>
    </section>
    <section class="w-full bg-[#fbfbfc] pt-32 dark:bg-[#1F232A]">
        <div class="w-full bg-[url(@/assets/svg/homepage-wave-bottom.svg)] bg-cover bg-top bg-no-repeat pb-8 dark:bg-[url(@/assets/svg/homepage-wave-bottom-dark.svg)]">
          <div class="pt-[5%]"></div>
          <div class="relative mx-auto flex w-full flex-col justify-between md:flex-row-reverse">
            <img
              class="my-auto size-full shadow-2xl dark:hidden md:w-1/2"
              src="@/assets/img/homepage-screenshot-2.png"
              :alt="$t('text.homepage.screenshotScheduleAlt')"
            />
            <img
              class="my-auto hidden size-full shadow-2xl dark:block md:w-1/2"
              src="@/assets/img/homepage-screenshot-2-dark.png"
              :alt="$t('text.homepage.screenshotScheduleAlt')"
            />
            <div class="flex-center my-20 flex-col md:w-[45%]">
              <p class="w-[70%] text-2xl font-light leading-loose tracking-wide">
                {{ $t('text.homepage.scheduleCopy') }}
              </p>
            </div>
          </div>
      </div>
    </section>
    <home-footer></home-footer>
  </div>
</template>
