import { createApp } from 'vue';
import useDayJS from '@/composables/dayjs';

/**
 * Mount a fake VueJS app
 * See: https://vuejs.org/guide/scaling-up/testing.html#testing-composables
 */
export default function withSetup() {
  const app = createApp({
    setup() {
      // suppress missing template warning
      return () => {};
    },
  });
  app.mount(document.createElement('div'));

  useDayJS(app, 'en');

  return app;
}
