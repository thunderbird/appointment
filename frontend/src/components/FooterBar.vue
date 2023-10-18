<template>
  <footer class="
    relative z-50 h-16 w-full -mt-16 px-4 shadow-lg border-t flex justify-between
    bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600
  ">
      <ul class="flex justify-center gap-8 w-full">
        <li class="
          flex text-base border-t-4 border-t-transparent transition-all ease-in-out
          text-gray-600 dark:text-gray-300 hover:border-t-gray-200 dark:hover:border-t-gray-400
        ">
          <router-link class="flex-center min-w-[120px]" :to="{ name: 'privacy' }" target="_blank">
            Privacy
          </router-link>
        </li>
        <li class="
          flex text-base border-t-4 border-t-transparent transition-all ease-in-out
          text-gray-600 dark:text-gray-300 hover:border-t-gray-200 dark:hover:border-t-gray-400
        ">
          <router-link class="flex-center min-w-[120px]" :to="{ name: 'terms' }" target="_blank">
            Legal
          </router-link>
        </li>
      </ul>
  </footer>
</template>
