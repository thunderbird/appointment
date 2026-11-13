import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import { createPinia } from 'pinia';
import dayjs from 'dayjs';
import i18ninstance from '@/composables/i18n';
import { dayjsKey } from '@/keys';
import { FtueStep } from '@/definitions';
import { useUserStore } from '@/stores/user-store';
import { useFTUEStore } from '@/stores/ftue-store';
import { useCalendarStore } from '@/stores/calendar-store';
import { useScheduleStore } from '@/stores/schedule-store';
import CreateBookingPageStep from '@/views/FTUEView/steps/CreateBookingPageStep.vue';
import withSetup from '../utils/with-setup';

describe('CreateBookingPageStep', () => {
  let app;
  let pinia;
  let wrapper;
  let scheduleStore;
  let ftueStore;

  const existingSchedule = {
    id: 42,
    name: 'Old booking page',
    calendar_id: 1,
    start_time: '10:00',
    end_time: '14:00',
    weekdays: [1, 3],
    slot_duration: 45,
  };

  const mountStep = () =>
    mount(CreateBookingPageStep, {
      global: {
        plugins: [pinia, i18ninstance],
        provide: { [dayjsKey]: dayjs },
      },
    });

  const clickContinue = async () => {
    await wrapper
      .findAll('button')
      .find((b) => b.text() === 'Continue')
      .trigger('click');
    await flushPromises();
  };

  beforeEach(() => {
    pinia = createPinia();
    app = withSetup().use(pinia);

    const user = useUserStore();
    user.data.username = 'tester';
    user.data.settings.timezone = 'UTC';

    const calendarStore = useCalendarStore();
    calendarStore.calendars = [
      { id: 1, title: 'Cal', connected: true },
      { id: 2, title: 'Other', connected: true },
    ];
    vi.spyOn(calendarStore, 'fetch').mockResolvedValue();
    vi.spyOn(calendarStore, 'connectCalendar').mockResolvedValue();

    ftueStore = useFTUEStore();
    vi.spyOn(ftueStore, 'moveToStep').mockResolvedValue();

    scheduleStore = useScheduleStore();
    vi.spyOn(scheduleStore, 'createSchedule').mockResolvedValue({});
    vi.spyOn(scheduleStore, 'updateSchedule').mockResolvedValue({});
    scheduleStore.isLoaded = true;
  });

  afterEach(() => {
    wrapper?.unmount();
    app?.unmount();
    vi.restoreAllMocks();
  });

  it('creates a schedule if the user has none yet', async () => {
    wrapper = mountStep();
    await clickContinue();

    expect(scheduleStore.createSchedule).toHaveBeenCalledOnce();
    expect(scheduleStore.updateSchedule).not.toHaveBeenCalled();
    expect(ftueStore.moveToStep).toHaveBeenCalledWith(FtueStep.SetAvailability);
  });

  it('updates the existing schedule instead of creating a new one', async () => {
    scheduleStore.schedules = [existingSchedule];

    wrapper = mountStep();
    await wrapper.find('input[name="bookingPageTitle"]').setValue('New booking page');
    await clickContinue();

    expect(scheduleStore.createSchedule).not.toHaveBeenCalled();
    expect(scheduleStore.updateSchedule).toHaveBeenCalledWith(existingSchedule.id, {
      ...existingSchedule,
      name: 'New booking page',
    });
    expect(ftueStore.moveToStep).toHaveBeenCalledWith(FtueStep.SetAvailability);
  });

  it('waits for the schedule to load and keeps its values, e.g. after a page reload', async () => {
    const scheduleOnSecondCalendar = { ...existingSchedule, calendar_id: 2 };
    scheduleStore.isLoaded = false;

    wrapper = mountStep();
    await clickContinue();
    expect(scheduleStore.createSchedule).not.toHaveBeenCalled();
    expect(scheduleStore.updateSchedule).not.toHaveBeenCalled();

    // Schedules finish loading after the first render
    scheduleStore.schedules = [scheduleOnSecondCalendar];
    scheduleStore.isLoaded = true;
    await flushPromises();
    await clickContinue();

    expect(scheduleStore.createSchedule).not.toHaveBeenCalled();
    expect(scheduleStore.updateSchedule).toHaveBeenCalledWith(scheduleOnSecondCalendar.id, scheduleOnSecondCalendar);
  });
});
