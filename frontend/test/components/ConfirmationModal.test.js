import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils'
import ConfirmationModal from '@/components/ConfirmationModal.vue';
import i18ninstance from '@/composables/i18n';


describe('ConfirmationModal', () => {
  var ourProps;
  var wrapper;

  beforeEach(() => {
    ourProps = {
      open: true,
      title: 'Confirm modal title',
      message: 'The confirm modal message goes here.',
      confirmLabel: 'Continue',
      cancelLabel: 'Cancel',
      useCautionButton: false,
    };
  });

  afterEach(() => {
    wrapper.unmount();
  });

  it('renders correctly when modal is open', () => {
    wrapper = mount(ConfirmationModal, {
      propsData: ourProps,
      global: {
        plugins: [i18ninstance], // install the i18ninstance as a global plugin
      },
    });
    expect(wrapper.props()).toEqual(ourProps);
  });

  it('renders correctly with closed state', () => {
    ourProps.open = false;
    wrapper = mount(ConfirmationModal, {
      propsData: ourProps,
      global: {
        plugins: [i18ninstance],
      },
    });
    expect(wrapper.props()).toEqual(ourProps);
  });

  it('renders correctly with caution button', () => {
    ourProps.useCautionButton = true;
    wrapper = mount(ConfirmationModal, {
      propsData: ourProps,
      global: {
        plugins: [i18ninstance],
      },
    });
    expect(wrapper.props()).toEqual(ourProps);
  });

  it('emits confirm event when click confirm button', async () => {
    wrapper = mount(ConfirmationModal, {
      propsData: ourProps,
      global: {
        plugins: [i18ninstance],
      },
    });
    const button = wrapper.find('.btn-confirm');
    await button.trigger('click');
    expect(wrapper.emitted().confirm, 'expected confirm event to have been emitted').toBeTruthy();
  });

  it('emits close event when click cancel button', async () => {
    wrapper = mount(ConfirmationModal, {
      propsData: ourProps,
      global: {
        plugins: [i18ninstance],
      },
    });
    const button = wrapper.find('.btn-close');
    await button.trigger('click');
    expect(wrapper.emitted().close, 'expected close event to have been emitted').toBeTruthy();
  });

  it('emits close event when click cancel button (caution button)', async () => {
    ourProps.useCautionButton = true;
    wrapper = mount(ConfirmationModal, {
      propsData: ourProps,
      global: {
        plugins: [i18ninstance],
      },
    });
    const button = wrapper.find('.btn-close');
    await button.trigger('click');
    expect(wrapper.emitted().close, 'expected close event to have been emitted').toBeTruthy();
  });
});
