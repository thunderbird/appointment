import {
  expect, test, beforeEach, describe,
} from 'vitest';
import { useUserActivityStore } from '@/stores/user-activity-store';
import { createPinia, setActivePinia } from 'pinia';
import { Dismissibles } from '@/definitions';

describe('User Activity Store', () => {
  // Create a pinia instance before each test
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  test('init', () => {
    const store = useUserActivityStore();
    expect(store.data.dismissedBetaWarning).toBe(false);
  });

  test('dismiss', () => {
    const store = useUserActivityStore();
    store.dismiss(Dismissibles.BetaWarning);
    expect(store.data.dismissedBetaWarning).toBe(true);
  });
});
