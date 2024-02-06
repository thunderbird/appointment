import { expect, test, beforeEach, describe } from 'vitest';
import { useSiteNotificationStore } from '@/stores/alert-store';
import { createPinia, setActivePinia } from 'pinia';

describe('Site Notifications Store', () => {
  // Create a pinia instance before each test
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  test('visible', () => {
    const alert = useSiteNotificationStore();
    alert.show(123, 'title', 'message', 'url');
    expect(alert.isVisible).toBe(true);
  });
  test('attributes', () => {
    const alert = useSiteNotificationStore();
    alert.show(123, 'title', 'message', 'url');
    expect(alert.title).toBe('title');
    expect(alert.actionUrl).toBe('url');
    expect(alert.message).toBe('message');
  });
  test('same', () => {
    const alert = useSiteNotificationStore();
    alert.show(123, 'title', 'message', 'url');
    expect(alert.isSame(123)).toBe(true);
  });
  test('invisible at start', () => {
    const alert = useSiteNotificationStore();
    expect(alert.isVisible).toBe(false);
  });
  test('invisible after reset', () => {
    const alert = useSiteNotificationStore();
    alert.show(123, 'title', 'message', 'url');
    alert.reset();
    expect(alert.isVisible).toBe(false);
  });
  test('lock', () => {
    const alert = useSiteNotificationStore();
    alert.lock(123);
    expect(alert.isVisible).toBe(false);
    expect(alert.isSame(123)).toBe(true);
  });
});
