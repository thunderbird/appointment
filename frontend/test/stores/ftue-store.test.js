import {
  expect, test, beforeEach, describe,
} from 'vitest';
import { useFTUEStore } from '@/stores/ftue-store';
import { createPinia, setActivePinia } from 'pinia';
import { FtueStep } from '@/definitions';

describe('FTUE Store', () => {
  // Create a pinia instance before each test
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  test('init', () => {
    const ftue = useFTUEStore();
    expect(ftue.currentStep).toBe(FtueStep.SetupProfile);
    expect(ftue.hasNextStep).toBe(true);
    expect(ftue.hasPreviousStep).toBe(false);
    expect(ftue.stepTitle).toBe('ftue.steps.setupProfile');
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
    ftue.nextStep();
    expect(ftue.currentStep).toBe(FtueStep.CalendarProvider);
    ftue.nextStep();
    expect(ftue.currentStep).toBe(FtueStep.ConnectCalendars);
    ftue.nextStep();
    expect(ftue.currentStep).toBe(FtueStep.SetupSchedule);
    ftue.nextStep();
    expect(ftue.currentStep).toBe(FtueStep.ConnectVideoConferencing);
    ftue.nextStep();
    expect(ftue.currentStep).toBe(FtueStep.Finish);
    ftue.nextStep();
    expect(ftue.currentStep).toBe(FtueStep.Finish);
    ftue.previousStep();
    expect(ftue.currentStep).toBe(FtueStep.ConnectVideoConferencing);
    ftue.previousStep();
    ftue.previousStep();
    ftue.previousStep();
    ftue.previousStep();
    expect(ftue.currentStep).toBe(FtueStep.SetupProfile);
  });
});
