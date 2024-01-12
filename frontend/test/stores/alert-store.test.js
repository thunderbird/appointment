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
    expect(alert.isVisible === true);
  });
  test('attributes', () => {
    const alert = useSiteNotificationStore();
    alert.show(123, 'title', 'message', 'url');
    expect(alert.title === 'title');
    expect(alert.actionUrl === 'url');
    expect(alert.message === 'message');
  });
  test('same', () => {
    const alert = useSiteNotificationStore();
    alert.show(123, 'title', 'message', 'url');
    expect(alert.isSameNotification(123) === true);
  });
  test('invisible at start', () => {
    const alert = useSiteNotificationStore();
    expect(alert.isVisible === false);
  });
  test('invisible after reset', () => {
    const alert = useSiteNotificationStore();
    alert.show(123, 'title', 'message', 'url');
    alert.reset();
    expect(alert.isVisible === false);
  });
  test('lock', () => {
    const alert = useSiteNotificationStore();
    alert.lock(123);
    expect(alert.isVisible === false);
    expect(alert.isSameNotification(123) === true);
  });
});
