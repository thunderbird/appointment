import {
  expect, test, beforeEach, describe,
} from 'vitest';
import { useBookingModalStore } from '@/stores/booking-modal-store';
import { createPinia, setActivePinia } from 'pinia';
import { ModalStates } from '@/definitions';

describe('Booking modal Store', () => {
  // Create a pinia instance before each test
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  test('open', () => {
    const store = useBookingModalStore();
    store.openModal();
    expect(store.open).toBe(true);
    expect(store.state).toBe(ModalStates.Open);
  });
  test('close', () => {
    const store = useBookingModalStore();
    store.closeModal();
    expect(store.open).toBe(false);
  });
  test('editable', () => {
    const store = useBookingModalStore();
    expect(store.isEditable).toBe(true);
    store.state = ModalStates.Error;
    expect(store.isEditable).toBe(true);
  });
  test('not editable', () => {
    const store = useBookingModalStore();
    store.state = ModalStates.Loading;
    expect(store.isEditable).toBe(false);
    store.state = ModalStates.Finished;
    expect(store.isEditable).toBe(false);
  });
});
