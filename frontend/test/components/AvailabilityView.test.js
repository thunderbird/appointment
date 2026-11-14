import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia } from 'pinia';
import { ref } from 'vue';
import i18ninstance from '@/composables/i18n';
import useDayJS from '@/composables/dayjs';
import { callKey } from '@/keys';
import AvailabilityView from '@/views/AvailabilityView/index.vue';
import { createAvailabilityStore } from '@/stores/availability-store';
import { NoticeBarTypes } from '@thunderbirdops/services-ui';

describe('AvailabilityView', () => {
  let wrapper;

  beforeEach(() => {
    window.scrollTo = vi.fn();
  });

  afterEach(() => {
    wrapper?.unmount();
  });

  const defaultCallMock = vi.fn().mockImplementation(() => ({
    get: () => ({
      json: () => Promise.resolve({ data: ref([]), error: ref(false) }),
    }),
    post: () => ({
      json: () => Promise.resolve({ data: ref({}), error: ref(false) }),
    }),
    put: () => ({
      json: () => Promise.resolve({ data: ref({}), error: ref(false) }),
    }),
    delete: () => ({
      json: () => Promise.resolve({ data: ref({}), error: ref(false) }),
    }),
  }));

  const createWrapper = (callMock = defaultCallMock) => {
    const pinia = createPinia();
    wrapper = mount(AvailabilityView, {
      global: {
        plugins: [
          pinia,
          i18ninstance,
          {
            install(app) {
              useDayJS(app, 'en');
            },
          },
        ],
        provide: {
          [callKey]: callMock,
        },
        stubs: {
          AvailabilitySettings: true,
          BookingPageDetails: true,
          BookingPageLink: true,
          LoadingSpinner: true,
        },
      },
    });
    const availabilityStore = createAvailabilityStore(callMock);
    return { wrapper, availabilityStore, pinia };
  };

  it('renders notices container when isDirty is true', async () => {
    const { wrapper, availabilityStore } = createWrapper();

    availabilityStore.$patch({
      isLoaded: true,
      initialState: { name: 'Initial' },
      currentState: { name: 'Changed' },
    });

    await wrapper.vm.$nextTick();

    const container = wrapper.find('.notices-container');
    expect(container.exists()).toBe(true);
    expect(container.text()).toContain('You have unsaved changes');
    expect(container.text()).toContain('Save changes');
    expect(container.text()).toContain('Revert changes');
  });

  it('displays both validation error and unsaved changes notice simultaneously in document flow', async () => {
    const { wrapper, availabilityStore } = createWrapper();

    availabilityStore.$patch({
      isLoaded: true,
      initialState: { name: 'Initial' },
      currentState: { name: 'Changed' },
    });

    // Simulate validation error on the component
    wrapper.vm.validationError = { title: 'End time should be at least 11:30.' };
    await wrapper.vm.$nextTick();

    const container = wrapper.find('.notices-container');
    expect(container.exists()).toBe(true);

    const noticeBars = container.findAllComponents({ name: 'NoticeBar' });
    expect(noticeBars).toHaveLength(2);

    // First notice bar is Critical validation error
    expect(noticeBars[0].props('type')).toBe(NoticeBarTypes.Critical);
    expect(noticeBars[0].text()).toContain('End time should be at least 11:30.');

    // Second notice bar is Warning unsaved changes CTA bar
    expect(noticeBars[1].props('type')).toBe(NoticeBarTypes.Warning);
    expect(noticeBars[1].text()).toContain('You have unsaved changes');
    expect(noticeBars[1].text()).toContain('Save changes');
    expect(noticeBars[1].text()).toContain('Revert changes');
  });

  it('clears validation error when close button is clicked and keeps CTA bar visible', async () => {
    const { wrapper, availabilityStore } = createWrapper();

    availabilityStore.$patch({
      isLoaded: true,
      initialState: { name: 'Initial' },
      currentState: { name: 'Changed' },
    });

    wrapper.vm.validationError = { title: 'End time should be at least 11:30.' };
    await wrapper.vm.$nextTick();

    // Click close button on error notice
    const closeBtn = wrapper.find('.notices-container .btn-close');
    expect(closeBtn.exists()).toBe(true);
    await closeBtn.trigger('click');
    await wrapper.vm.$nextTick();

    // Error is gone, but unsaved changes CTA remains
    expect(wrapper.vm.validationError).toBeNull();
    const noticeBars = wrapper.findAllComponents({ name: 'NoticeBar' });
    expect(noticeBars).toHaveLength(1);
    expect(noticeBars[0].props('type')).toBe(NoticeBarTypes.Warning);
    expect(noticeBars[0].text()).toContain('Save changes');
  });

  it('displays success notice when save succeeds and isDirty is false', async () => {
    const { wrapper, availabilityStore } = createWrapper();

    availabilityStore.$patch({
      isLoaded: true,
      initialState: { name: 'Initial' },
      currentState: { name: 'Initial' },
    });

    wrapper.vm.saveSuccess = { title: 'Availability saved successfully.' };
    await wrapper.vm.$nextTick();

    const container = wrapper.find('.notices-container');
    expect(container.exists()).toBe(true);

    const noticeBars = container.findAllComponents({ name: 'NoticeBar' });
    expect(noticeBars).toHaveLength(1);
    expect(noticeBars[0].props('type')).toBe(NoticeBarTypes.Success);
    expect(noticeBars[0].text()).toContain('Availability saved successfully.');
  });

  it('keeps unsaved changes CTA visible below error when clicking Save changes fails validation', async () => {
    const { wrapper, availabilityStore } = createWrapper();

    availabilityStore.$patch({
      isLoaded: true,
      initialState: { name: 'Initial' },
      currentState: { name: '' },
    });

    await wrapper.vm.$nextTick();

    const primaryButtons = wrapper.findAllComponents({ name: 'PrimaryButton' });
    expect(primaryButtons.length).toBeGreaterThan(0);
    await primaryButtons[0].trigger('click');
    await wrapper.vm.$nextTick();

    const container = wrapper.find('.notices-container');
    expect(container.exists()).toBe(true);

    const noticeBars = container.findAllComponents({ name: 'NoticeBar' });
    expect(noticeBars).toHaveLength(2);

    expect(noticeBars[0].props('type')).toBe(NoticeBarTypes.Critical);
    expect(noticeBars[1].props('type')).toBe(NoticeBarTypes.Warning);
    expect(noticeBars[1].text()).toContain('Save changes');
    expect(noticeBars[1].text()).toContain('Revert changes');
  });

  it('clears notices and resets dirty state when Revert changes is clicked', async () => {
    const { wrapper, availabilityStore } = createWrapper();

    availabilityStore.$patch({
      isLoaded: true,
      initialState: { name: 'Initial' },
      currentState: { name: '' },
    });

    await wrapper.vm.$nextTick();

    // Trigger error by clicking Save changes
    const primaryButtons = wrapper.findAllComponents({ name: 'PrimaryButton' });
    await primaryButtons[0].trigger('click');
    await wrapper.vm.$nextTick();
    expect(wrapper.find('.notices-container').exists()).toBe(true);

    // Click Revert changes button
    const linkButtons = wrapper.findAllComponents({ name: 'LinkButton' });
    expect(linkButtons.length).toBeGreaterThan(0);
    await linkButtons[0].trigger('click');
    await wrapper.vm.$nextTick();

    // Everything is cleared and notices container unmounts
    expect(wrapper.vm.validationError).toBeNull();
    expect(wrapper.find('.notices-container').exists()).toBe(false);
  });
});
