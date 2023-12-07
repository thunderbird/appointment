<template>
  <div>
    <section>
      <div class="flex-center flex-col gap-12 mt-8">
        <img class="w-full max-w-xs md:max-w-sm lg:max-w-md" src="/appointment_logo.svg" alt="Appointment Logo" />
        <h2 class="pt-6 font-display tracking-[0.19em] uppercase text-center text-lg md:text-3xl lg:text-5xl">
          {{ $t('app.title') }}
        </h2>
        <div class="-mb-12 md:-mb-20 lg:-mb-28 xl:-mb-40 flex flex-col flex-center">
          <h4 class="text-xl tracking-wide leading-9 pt-12 font-light max-w-2xl text-center">
            {{ $t('text.homepage.intro') }}
          </h4>
          <div class="mt-16">
            <primary-button v-if="!isAuthenticated" :label="$t('label.logIn')" @click="login" />
            <primary-button v-else-if="isAuthenticated" :label="$t('label.continue')" @click="enter" />
          </div>
        </div>
        <div class="w-full">
          <!-- Padding top is rounded up aspect ratio percentage (height / width) of image -->
          <div class="bg-[url(@/assets/svg/homepage-split.svg)]
          dark:bg-[url(@/assets/svg/homepage-split-dark.svg)]
          bg-no-repeat bg-contain h-0 pt-[14%] w-full"
          ></div>
        </div>
      </div>
    </section>
    <section class="mx-4">
      <h2 class="text-3xl pb-16 pt-16 text-center text-teal-600 dark:text-teal-400">
        {{ $t('text.homepage.sectionHeader') }}
      </h2>
      <section class="flex flex-col gap-16 justify-center mx-auto max-w-full md:flex-row md:max-w-7xl">
        <InfoBox :title="$t('text.homepage.planEventTitle')">{{ $t('text.homepage.planEventBody') }}</InfoBox>
        <InfoBox :title="$t('text.homepage.setAvailabilityTitle')">{{ $t('text.homepage.setAvailabilityBody') }}</InfoBox>
        <InfoBox :title="$t('text.homepage.shareWithOthersTitle')">{{ $t('text.homepage.shareWithOthersBody') }}</InfoBox>
      </section>
    </section>
    <section class="w-full">
        <div class="bg-[url(@/assets/svg/homepage-wave.svg)]
        dark:bg-[url(@/assets/svg/homepage-wave-dark.svg)]
        bg-top bg-no-repeat bg-cover w-full"
        >
          <div class="pt-[13%]"></div>
          <div class="w-full flex flex-col md:flex-row relative mx-auto justify-between">
            <img class="shadow-2xl my-auto h-full w-full md:w-1/2 dark:hidden"
                 src="@/assets/img/homepage-screenshot.png"
                 :alt="$t('text.homepage.screenshotCalendarAlt')"
            />
            <img class="shadow-2xl my-auto h-full w-full md:w-1/2 hidden dark:block"
                 src="@/assets/img/homepage-screenshot-dark.png"
                 :alt="$t('text.homepage.screenshotCalendarAlt')"
            />
            <div class="flex-col mb-20 mt-20 md:w-[45%] flex-center">
              <p class="text-2xl tracking-wide leading-loose font-light w-[70%]">
                {{ $t('text.homepage.calendarCopy') }}
              </p>
            </div>
          </div>
        </div>
    </section>
    <section class="w-full pt-32 bg-[#fbfbfc] dark:bg-[#1F232A]">
        <div class="bg-[url(@/assets/svg/homepage-wave-bottom.svg)] dark:bg-[url(@/assets/svg/homepage-wave-bottom-dark.svg)] bg-top bg-no-repeat bg-cover w-full pb-8">
          <div class="pt-[5%]"></div>
          <div class="w-full flex flex-col md:flex-row-reverse relative mx-auto justify-between">
            <img class="shadow-2xl my-auto h-full w-full md:w-1/2 dark:hidden"
                 src="@/assets/img/homepage-screenshot-2.png"
                 :alt="$t('text.homepage.screenshotScheduleAlt')"
            />
            <img class="shadow-2xl my-auto h-full w-full md:w-1/2 hidden dark:block"
                 src="@/assets/img/homepage-screenshot-2-dark.png"
                 :alt="$t('text.homepage.screenshotScheduleAlt')"
            />
            <div class="flex-col mb-20 mt-20 md:w-[45%] flex-center">
              <p class="text-2xl tracking-wide leading-loose font-light w-[70%]">
                {{ $t('text.homepage.scheduleCopy') }}
              </p>
            </div>
          </div>
      </div>
    </section>
    <HomeFooter></HomeFooter>
  </div>
</template>

<script setup>
import { inject, onMounted} from 'vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import InfoBox from '@/elements/home/InfoBox.vue';
import HomeFooter from '@/components/HomeFooter.vue';
import { useUserStore } from '@/stores/user-store';
import { useRouter } from 'vue-router';

const refresh = inject('refresh');
<<<<<<< HEAD
const router = useRouter();
=======
const login = inject('login');
>>>>>>> main

const isAuthenticated = useUserStore().exists();

const enter = () => {
  router.push('/calendar');
};
const login = () => {
  router.push('/login');
};

// initially load data when component gets remounted
onMounted(async () => {
  await refresh();
});
</script>
