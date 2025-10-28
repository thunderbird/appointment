import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils'
import TabBar from '@/components/TabBar.vue';
import i18ninstance from '@/composables/i18n';


describe('TabBar', () => {
  var ourProps;
  var wrapper;

  const tabItems = [
    '12hAmPm', // just some random values from src/locales/en
    '24h',
    'allDay',
    'nextWeek',
    'previousWeek',
  ];

  beforeEach(() => {
    ourProps = {
      tabItems: tabItems,
      active: 2, // value of active tab
      disabled: false,
    };
  });

  afterEach(() => {
    wrapper.unmount();
  });

  it('renders correctly', () => {
    wrapper = mount(TabBar, {
      propsData: ourProps,
      global: {
        plugins: [i18ninstance],
      },
    });
    expect(wrapper.props()).toEqual(ourProps);
  });

  it('renders correctly when toggle is disabled', () => {
    ourProps.disabled = true;
    wrapper = mount(TabBar, {
      propsData: ourProps,
      global: {
        plugins: [i18ninstance],
      },
    });
    expect(wrapper.props()).toEqual(ourProps);
  });

  it('emits correct key event when a tab item is selected', async () => {
    wrapper = mount(TabBar, {
      propsData: ourProps,
      global: {
        plugins: [i18ninstance],
      },
    });
    const tabItem = wrapper.find('[data-testid=booking-' + tabItems[3] + '-btn]');
    await tabItem.trigger('click');
    expect(wrapper.emitted().update, 'expected update event to have been emitted').toBeTruthy();
    expect(wrapper.emitted().update[0][0], 'expected update event to contain correct tabItem').toBe(3);
  });

  it('does not emit update event when click on disabled tab item', async () => {
    ourProps.disabled = true;
    wrapper = mount(TabBar, {
      propsData: ourProps,
      global: {
        plugins: [i18ninstance],
      },
    });
    const tabItem = wrapper.find('[data-testid=booking-' + tabItems[3] + '-btn]');
    await tabItem.trigger('click');
    expect(wrapper.emitted().update, 'should not have received an update event when click on disabled tab item').toBeUndefined();
    expect(wrapper.emitted().click, 'expected click event to have been emitted').toBeTruthy();
  });
});
