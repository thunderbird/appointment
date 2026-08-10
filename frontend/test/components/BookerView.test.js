import { afterEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import { createPinia } from 'pinia';
import { ref } from 'vue';
import dayjs from 'dayjs';
import i18ninstance from '@/composables/i18n';
import { callKey, dayjsKey } from '@/keys';
import BookerView from '@/views/BookerView/index.vue';

describe('BookerView', () => {
  let wrapper;

  afterEach(() => {
    wrapper?.unmount();
  });

  it('shows the backend message for an invalid booking link', async () => {
    const response = {
      data: ref({
        detail: {
          id: 'INVALID_LINK',
          message: 'This link is no longer valid.',
        },
      }),
      error: ref(true),
    };
    const json = vi.fn().mockResolvedValue(response);
    const post = vi.fn().mockReturnValue({ json });
    const call = vi.fn().mockReturnValue({ post });

    wrapper = mount(BookerView, {
      global: {
        plugins: [createPinia(), i18ninstance],
        provide: {
          [callKey]: call,
          [dayjsKey]: dayjs,
        },
      },
    });

    await flushPromises();

    expect(call).toHaveBeenCalledWith('schedule/public/availability');
    expect(post).toHaveBeenCalledWith({ url: window.location.href.split('#')[0] });
    expect(wrapper.get('h1').text()).toBe('');
    expect(wrapper.get('p').text()).toBe('This link is no longer valid.');
  });
});
