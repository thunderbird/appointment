import { afterEach, describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia } from 'pinia';
import i18ninstance from '@/composables/i18n';
import useDayJS from '@/composables/dayjs';
import { useUserStore } from '@/stores/user-store';
import DateRequestedAppointmentItem from '@/views/BookingsView/components/DateRequestedAppointmentItem.vue';
import withSetup from '../utils/with-setup';

describe('DateRequestedAppointmentItem', () => {
  let wrapper;
  let app;

  afterEach(() => {
    wrapper?.unmount();
    app?.unmount();
  });

  it('shows the request date in the settings timezone', () => {
    // The user store needs an app context providing dayjs
    const pinia = createPinia();
    app = withSetup();
    app.use(pinia);
    useUserStore().data.settings.timezone = 'Europe/London';

    // 02:30 doesn't exist in America/Vancouver (system timezone in tests) on this day due to the DST change
    wrapper = mount(DateRequestedAppointmentItem, {
      props: {
        appointment: {
          time_created: '2026-03-08T02:30:00',
          slots: [{ start: '2026-03-10T10:00:00Z', attendee: { name: 'Name', email: 'name@example.com' } }],
        },
      },
      global: {
        plugins: [pinia, i18ninstance, { install: (app) => useDayJS(app, 'en') }],
      },
    });

    expect(wrapper.text()).toContain('03/08/2026, 2:30 AM');
  });
});
