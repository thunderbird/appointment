<template>
  <section class="flex flex-col bg-gray-700 p-4 lg:p-8">
    <div class="flex-center mb-16">
      <div class="flex items-center gap-3">
        <img class="mr-2 h-8 pl-4" src="/appointment_logo.svg" alt="Appointment Logo"/>
        <div class="font-display text-lg uppercase tracking-[.25em] text-white">
          Thunderbird Appointment
        </div>
      </div>
    </div>
    <div class="flex-center mb-0 mt-auto">
      <ul class="flex w-full justify-center gap-16">
        <li class="
          flex border-t-4 border-t-transparent text-base text-gray-300 transition-all
          ease-in-out dark:text-gray-300
        ">
          <router-link class="flex-center" :to="{ name: 'privacy' }" target="_blank">
            {{ $t('label.privacy') }}
          </router-link>
        </li>
        <li class="
          flex border-t-4 border-t-transparent text-base text-gray-300 transition-all
          ease-in-out dark:text-gray-300
        ">
          <router-link class="flex-center" :to="{ name: 'terms' }" target="_blank">
            {{ $t('label.legal') }}
          </router-link>
        </li>
      </ul>
    </div>
    <div class="flex-center mb-0 mt-8 text-center text-gray-300">
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
