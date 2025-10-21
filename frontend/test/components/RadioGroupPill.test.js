import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing';
import i18ninstance from '@/composables/i18n';
import router from '@/router';
import withSetup from '../utils/with-setup';
import RadioGroupPill from '@/components/RadioGroupPill.vue';


describe('RadioGroupPill', () => {
  var app;
  var wrapper;

  var radioOpts = [ 'choice1', 'choice2', 'choice3' ];
  const ourProps = {
    legend: 'Legend goes here',
    name: 'Radio group name',
    disabled: false,
    options: radioOpts,
  };

  // create a pinia instance before each test as the RadioGroup uses the UserStore
  beforeEach(() => {
    app = withSetup();
    app.use(createTestingPinia());
  });

  afterEach(() => {
    wrapper.unmount();
  });

  it('renders correctly when enabled', async () => {
    wrapper = mount(RadioGroupPill, {
      propsData: ourProps,
      global: {
        // the RadioGroup uses i18n and rounter-link so install these global component plugins
        plugins: [i18ninstance, router],
      },
    });
    expect(wrapper.props().legend, 'expected radio group legend to be correct').toEqual(ourProps.legend);
    expect(wrapper.props().name, 'expected radio group name to be correct').toEqual(ourProps.name);
    expect(wrapper.props().options, 'expected radio group options to be correct').toEqual(radioOpts);
    expect(wrapper.props().disabled, 'expected radio group to be enabled').toBeFalsy();
    const radioInput = wrapper.find('input[type="radio"]');
    expect(radioInput.exists()).toBeTruthy();
  });

  it('renders correctly when disabled', async () => {
    ourProps.disabled = true;
    wrapper = mount(RadioGroupPill, {
      propsData: ourProps,
      global: {
        // the RadioGroup uses i18n and rounter-link so install these global component plugins
        plugins: [i18ninstance, router],
      },
    });
    expect(wrapper.props().legend, 'expected radio group legend to be correct').toEqual(ourProps.legend);
    expect(wrapper.props().name, 'expected radio group name to be correct').toEqual(ourProps.name);
    expect(wrapper.props().options, 'expected radio group options to be correct').toEqual(radioOpts);
    expect(wrapper.props().disabled, 'expected radio group to be disabled').toBeTruthy();
    const radioInput = wrapper.find('input[type="radio"]');
    expect(radioInput.exists()).toBeTruthy();
  });
});
