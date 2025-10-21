import { vi, describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils'
import ExternalRedirect from '@/components/ExternalRedirect.vue';
import i18ninstance from '@/composables/i18n';


describe('ExternalRedirect', () => {
  it('renders correctly', () => {
    var ourProps = {
        redirectUrl: 'tb.pro',
    }

    // mock the window.location object for specific properties that the component will call
    vi.stubGlobal('location', {
      assign: vi.fn(),
      replace: vi.fn(),
      href: 'http://localhost/', // Set a default value if needed
    });

    const wrapper = mount(ExternalRedirect, {
      propsData: ourProps,
      global: {
        plugins: [i18ninstance],
      },
    });

    // verify the redirect link was created
    expect(wrapper.props()).toEqual(ourProps);
    const linkWrapper = wrapper.find('a');
    expect(linkWrapper.exists()).toBe(true);
    expect(linkWrapper.text()).toBe(ourProps.redirectUrl);
    expect(linkWrapper.attributes('href')).toBe(ourProps.redirectUrl);

    // clean up our mock and unmount the component
    vi.unstubAllGlobals()
    wrapper.unmount();
  });
});
