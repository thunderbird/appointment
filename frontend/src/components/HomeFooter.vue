<template>
  <section class="bg-gray-700 p-4 lg:p-8 flex flex-col">
    <div class="flex-center mb-16">
      <div class="flex gap-3 items-center">
        <img class="h-8 mr-2 pl-4" src="/appointment_logo.svg" alt="Appointment Logo"/>
        <div class="text-lg font-display tracking-[.25em] text-white uppercase">
          Thunderbird Appointment
        </div>
      </div>
    </div>
    <div class="flex-center mb-0 mt-auto">
      <ul class="flex justify-center w-full gap-16">
        <li class="
          flex text-base border-t-4 border-t-transparent transition-all ease-in-out
          text-gray-300 dark:text-gray-300
        ">
          <router-link class="flex-center" :to="{ name: 'privacy' }" target="_blank">
            {{ $t('label.privacy') }}
          </router-link>
        </li>
        <li class="
          flex text-base border-t-4 border-t-transparent transition-all ease-in-out
          text-gray-300 dark:text-gray-300
        ">
          <router-link class="flex-center" :to="{ name: 'terms' }" target="_blank">
            {{ $t('label.legal') }}
          </router-link>
        </li>
      </ul>
    </div>
    <div class="flex-center mb-0 mt-8 text-gray-300 text-center">
      <p class="md:w-1/2">
        <i18n-t keypath="text.homepage.copywrite">
          <template v-slot:mzlaLink>
            <a class="underline underline-offset-2"
               href="https://blog.thunderbird.net/2020/01/thunderbirds-new-home/"
            >
              {{ $t('text.homepage.mzlaLinkText') }}
            </a>
          </template>
          <template v-slot:creativeCommonsLink>
            <a class="underline underline-offset-2"
               href="https://www.mozilla.org/en-US/foundation/licensing/website-content/"
            >
              {{ $t('text.homepage.creativeCommonsLinkText') }}
            </a>
          </template>
        </i18n-t>
      </p>
    </div>
  </section>
</template>
