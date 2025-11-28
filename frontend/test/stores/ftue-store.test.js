import {
  expect, test, beforeEach, describe, vi,
} from 'vitest';
import { useFTUEStore } from '@/stores/ftue-store';
import { createPinia, setActivePinia } from 'pinia';
import { FtueStep } from '@/definitions';

// Mock vue-router as moveToStep uses it to navigate to the next step
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
  }),
  useRoute: () => ({
    query: {},
  }),
}));

describe('FTUE Store', () => {
  // Create a pinia instance before each test
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  test('init', () => {
    const ftue = useFTUEStore();
    expect(ftue.currentStep).toBe(FtueStep.SetupProfile);
  });

  test('messages', () => {
    const ftue = useFTUEStore();
    expect(ftue.infoMessage).toBeNull();
    expect(ftue.errorMessage).toBeNull();
    expect(ftue.warningMessage).toBeNull();

    ftue.infoMessage = { title: 'info' };
    ftue.errorMessage = { title: 'error', details: 'something went wrong' };
    ftue.warningMessage = { title: 'warning' };

    expect(ftue.infoMessage.title).toBe('info');
    expect(ftue.errorMessage.details).toBe('something went wrong');
    expect(ftue.warningMessage).not.toBeNull();

    ftue.$reset();

    expect(ftue.infoMessage).toBeNull();
    expect(ftue.errorMessage).toBeNull();
    expect(ftue.warningMessage).toBeNull();
  });

  test('steps', () => {
    const ftue = useFTUEStore();
    expect(ftue.currentStep).toBe(FtueStep.SetupProfile);
    ftue.moveToStep(FtueStep.ConnectCalendars);
    expect(ftue.currentStep).toBe(FtueStep.ConnectCalendars);
    ftue.moveToStep(FtueStep.ConnectCalendarsCalDav);
    expect(ftue.currentStep).toBe(FtueStep.ConnectCalendarsCalDav);
    ftue.moveToStep(FtueStep.ConnectCalendarsGoogle);
    expect(ftue.currentStep).toBe(FtueStep.ConnectCalendarsGoogle);
    ftue.moveToStep(FtueStep.CreateBookingPage);
    expect(ftue.currentStep).toBe(FtueStep.CreateBookingPage);
    ftue.moveToStep(FtueStep.SetAvailability);
    expect(ftue.currentStep).toBe(FtueStep.SetAvailability);
    ftue.moveToStep(FtueStep.VideoMeetingLink);
    expect(ftue.currentStep).toBe(FtueStep.VideoMeetingLink);
    ftue.moveToStep(FtueStep.SetupComplete);
    expect(ftue.currentStep).toBe(FtueStep.SetupComplete);
  });
});
