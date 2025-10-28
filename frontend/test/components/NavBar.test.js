import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing';
import i18ninstance from '@/composables/i18n';
import router from '@/router';
import withSetup from '../utils/with-setup';
import { useUserStore } from '@/stores/user-store';
import { RouterLink } from 'vue-router';
import NavBar from '@/components/NavBar.vue';


describe('NavBar', () => {
  var app;
  var wrapper;

  // list of route names that are also lang keys (format: label.<key>), used as nav items
  // these routes are added in addition to the routes already specified in NavBar.vue
  var navItems = [
    'schedule',
    'bookings',
  ];
  const ourProps = {
    navItems: navItems,
  };

  beforeEach(() => {
    app = withSetup();
    app.use(createTestingPinia());
  });

  afterEach(() => {
    wrapper.unmount();
  });

  it('renders correctly when not logged in', () => {
    wrapper = mount(NavBar, {
      propsData: ourProps,
      global: {
        plugins: [i18ninstance, router],
      },
    });

    // verify all expected router-link child components were rendered (only one when not signed in)
    const allRouterLinks = wrapper.findAllComponents(RouterLink);
    var foundLinks = [];
    for (let link of allRouterLinks) {
      foundLinks.push(link.props().to);
    }
    expect(foundLinks.length).toBe(1);
    expect(foundLinks[0]['name'], 'expected link component to be rendered').toBe('home');
  });

  it('renders correctly when logged in', () => {
    // fake sign-in via user store
    const user = useUserStore();
    user.data.accessToken = 'abc';
    expect(user.authenticated).toBe(true);

    wrapper = mount(NavBar, {
      propsData: ourProps,
      global: {
        plugins: [i18ninstance, router],
      },
    });

    // verify all expected router-link child components were rendered when signed in
    const allRouterLinks = wrapper.findAllComponents(RouterLink);
    var foundLinks = [];
    for (let link of allRouterLinks) {
      foundLinks.push(link.props().to.name);
    }
    // we expect the routes we sent in above in ourProps navItems as well as the other routes in
    // NavBar.vue that appear when the user is signed in
    const expRoutes = navItems.concat(['dashboard', 'profile', 'report-bug', 'contact', 'logout']);
    expect(foundLinks.length).toBe(expRoutes.length);
    for (let expRoute of expRoutes) {
      expect(foundLinks, 'expected link component to be rendered').toContain(expRoute);
    }
  });

  it('able to click the copy link button', async () => {
    // we need to mock the clipboard so the rendered component can copy to clipboard
    Object.defineProperty(navigator, 'clipboard', {
      value: {
        writeText: vi.fn(() => Promise.resolve()),
        readText: vi.fn(() => Promise.resolve('Mocked content')),
      },
      configurable: true,
    });

    // fake sign-in via user store and setup a fake copy link
    const user = useUserStore();
    user.data.accessToken = 'abc';
    user.myLink = 'https://stage.apt.mt/fakeuser/6e16a160/';
    expect(user.authenticated).toBe(true);

    wrapper = mount(NavBar, {
      propsData: ourProps,
      global: {
        plugins: [i18ninstance, router],
      },
    });

    // now click the copy link button and verify the link was written to the clipboard
    const copyLinkBtn = wrapper.find('.nav-copy-link-button');
    await copyLinkBtn.trigger('click');
    expect(navigator.clipboard.writeText).toHaveBeenCalledTimes(1);
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(user.myLink);

    // remove our mocked clipboard as it will persist between tests
    delete navigator.clipboard;
  });
});
