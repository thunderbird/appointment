import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia } from 'pinia';
import { ref } from 'vue';
import i18ninstance from '@/composables/i18n';
import useDayJS from '@/composables/dayjs';
import { callKey } from '@/keys';
import AvailabilityView from '@/views/AvailabilityView/index.vue';
import { useAvailabilityStore } from '@/stores/availability-store';
import { NoticeBarTypes } from '@thunderbirdops/services-ui';

describe('AvailabilityView', () => {
  let wrapper;
  let store;

  beforeEach(() => {
    window.scrollTo = vi.fn();
    const callMock = vi.fn().mockReturnValue({
      get: () => ({ json: () => Promise.resolve({ data: ref([]), error: ref(false) }) }),
      post: () => ({ json: () => Promise.resolve({ data: ref({}), error: ref(false) }) }),
      put: () => ({ json: () => Promise.resolve({ data: ref({}), error: ref(false) }) }),
      delete: () => ({ json: () => Promise.resolve({ data: ref({}), error: ref(false) }) }),
    });

    const pinia = createPinia();
    // Provide an already-loaded store before mounting so createAvailabilityStore does not trigger background init()
    store = useAvailabilityStore(pinia);
    store.isLoaded = true;
    store.initialState = { name: 'Initial' };
    store.currentState = { name: 'Initial' };

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
  });

  afterEach(() => {
    wrapper?.unmount();
  });

  const markDirty = async (name = 'Changed') => {
    store.currentState = { name };
    await wrapper.vm.$nextTick();
  };

  const getNoticeBars = () => wrapper.find('.notices-container').findAllComponents({ name: 'NoticeBar' });

  it('renders unsaved changes notice when form is dirty', async () => {
    await markDirty();

    const container = wrapper.find('.notices-container');
    expect(container.exists()).toBe(true);
    expect(container.text()).toContain('You have unsaved changes');
    expect(container.text()).toContain('Save changes');
  });

  it('displays validation error and unsaved changes notice together in document flow', async () => {
    await markDirty();

    wrapper.vm.validationError = { title: 'End time should be at least 11:30.' };
    await wrapper.vm.$nextTick();

    const bars = getNoticeBars();
    expect(bars).toHaveLength(2);
    expect(bars[0].props('type')).toBe(NoticeBarTypes.Critical);
    expect(bars[0].text()).toContain('End time should be at least 11:30.');
    expect(bars[1].props('type')).toBe(NoticeBarTypes.Warning);
    expect(bars[1].text()).toContain('Save changes');
  });

  it('clears error on close while keeping unsaved changes CTA visible', async () => {
    await markDirty();

    wrapper.vm.validationError = { title: 'Error message' };
    await wrapper.vm.$nextTick();

    await wrapper.find('.notices-container .btn-close').trigger('click');
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.validationError).toBeNull();
    const bars = getNoticeBars();
    expect(bars).toHaveLength(1);
    expect(bars[0].props('type')).toBe(NoticeBarTypes.Warning);
  });

  it('displays success notice when saved and form is not dirty', async () => {
    wrapper.vm.saveSuccess = { title: 'Saved successfully.' };
    await wrapper.vm.$nextTick();

    const bars = getNoticeBars();
    expect(bars).toHaveLength(1);
    expect(bars[0].props('type')).toBe(NoticeBarTypes.Success);
  });

  it('excludes success notice while validation error exists even if form is not dirty', async () => {
    wrapper.vm.saveSuccess = { title: 'Saved successfully.' };
    wrapper.vm.validationError = { title: 'Some error' };
    await wrapper.vm.$nextTick();

    const bars = getNoticeBars();
    expect(bars).toHaveLength(1);
    expect(bars[0].props('type')).toBe(NoticeBarTypes.Critical);
    expect(wrapper.text()).not.toContain('Saved successfully.');
  });

  it('handles Save and Revert user interactions properly', async () => {
    // 1. Invalid schedule triggers validation error without hiding CTA
    await markDirty('');
    await wrapper.findComponent({ name: 'PrimaryButton' }).trigger('click');
    await wrapper.vm.$nextTick();

    expect(getNoticeBars()).toHaveLength(2);

    // 2. Reverting changes clears all notices and unmounts container
    await wrapper.findComponent({ name: 'LinkButton' }).trigger('click');
    await wrapper.vm.$nextTick();

    expect(wrapper.find('.notices-container').exists()).toBe(false);
  });
});
