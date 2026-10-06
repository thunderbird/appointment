import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import i18ninstance from '@/composables/i18n';
import router from '@/router';
import withSetup from '../utils/with-setup';
import { useUserStore } from '@/stores/user-store';
import { RouterLink } from 'vue-router';
import { isDark } from '@/composables/useColourScheme';
import UserMenu from '@/components/UserMenu.vue';
import NavBarMobile from '@/components/NavBarMobile.vue';

describe('NavBarMobile', () => {
  var app;
  var wrapper;

  const getMountOptions = () => ({
    global: {
      plugins: [i18ninstance, router],
    },
  });

  beforeEach(() => {
    app = withSetup();
    app.use(createTestingPinia());
  });

  afterEach(() => {
    wrapper.unmount();
  });

  it('renders correctly when not logged in', () => {
    wrapper = mount(NavBarMobile, getMountOptions());

    // verify all expected router-link child components were rendered (only one when not signed in)
    const allRouterLinks = wrapper.findAllComponents(RouterLink);
    var foundLinks = [];
    for (let link of allRouterLinks) {
      foundLinks.push(link.props().to);
    }
    expect(foundLinks.length).toBe(1);
    expect(foundLinks[0]['name'], 'expected link component to be rendered').toBe('home');

    // the user menu is only available when signed in
    expect(wrapper.findComponent(UserMenu).exists()).toBe(false);
  });

  it('renders correctly when logged in and menu is closed', () => {
    // fake sign-in via user store
    const user = useUserStore();
    user.data.accessToken = 'abc';
    expect(user.authenticated).toBe(true);

    wrapper = mount(NavBarMobile, getMountOptions());

    // verify all expected router-link child components were rendered (only one when menu is closed)
    const allRouterLinks = wrapper.findAllComponents(RouterLink);
    var foundLinks = [];
    for (let link of allRouterLinks) {
      foundLinks.push(link.props().to);
    }
    expect(foundLinks.length).toBe(1);
    expect(foundLinks[0]['name'], 'expected link component to be rendered').toBe('dashboard');
  });

  it('renders correctly when logged in and menu is opened', async () => {
    // fake sign-in via user store
    const user = useUserStore();
    user.data.accessToken = 'abc';
    expect(user.authenticated).toBe(true);

    wrapper = mount(NavBarMobile, getMountOptions());

    // click to open/show the menu
    const menuButton = wrapper.find('button[aria-label="Open menu"]');
    await menuButton.trigger('click');

    // verify all expected router-link child components were rendered when signed in and menu is now shown
    const expectedLinks = [
      'dashboard', // there are two dashboard router-link child components
      'dashboard',
      'bookings',
      'availability',
      'settings',
    ];

    const allRouterLinks = wrapper.findAllComponents(RouterLink);
    var foundLinks = [];
    for (let link of allRouterLinks) {
      if (link.props().to.name) {
        foundLinks.push(link.props().to.name);
      } else {
        foundLinks.push(link.props().to);
      }
    }
    expect(foundLinks.length).toBe(expectedLinks.length);
    for (let expLink of expectedLinks) {
      expect(foundLinks, 'expected link component to be rendered').toContain(expLink);
    }
  });

  it('renders the user menu in the closed header when logged in', () => {
    const user = useUserStore();
    user.data.accessToken = 'abc';

    wrapper = mount(NavBarMobile, getMountOptions());

    expect(wrapper.findComponent(UserMenu).exists(), 'expected user menu to be rendered').toBe(true);
  });

  it('renders the switch theme item between availability and settings and toggles the theme', async () => {
    const user = useUserStore();
    user.data.accessToken = 'abc';

    wrapper = mount(NavBarMobile, getMountOptions());
    await wrapper.find('button[aria-label="Open menu"]').trigger('click');

    const labels = wrapper.findAll('.menu-content-container ul li').map((li) => li.text());
    const themeIdx = labels.indexOf('Switch theme');
    expect(themeIdx, 'expected switch theme item to be rendered').toBeGreaterThan(-1);
    expect(labels[themeIdx - 1]).toBe('Availability');
    expect(labels[themeIdx + 1]).toBe('Settings');

    const before = isDark.value;
    await wrapper.find('.theme-toggle').trigger('click');
    expect(isDark.value).toBe(!before);
    expect(wrapper.find('.menu-content-container').exists(), 'expected menu to stay open').toBe(true);

    // restore so the persisted preference doesn't leak between tests
    isDark.value = before;
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

    wrapper = mount(NavBarMobile, getMountOptions());

    // need to open the menu in order to access the copy link option
    const menuButton = wrapper.find('button[aria-label="Open menu"]');
    await menuButton.trigger('click');

    // now click the copy link button and verify the link was written to the clipboard
    const copyLinkBtn = wrapper.find('.share-link-button');
    await copyLinkBtn.trigger('click');
    expect(navigator.clipboard.writeText).toHaveBeenCalledTimes(1);
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(user.myLink);

    // remove our mocked clipboard as it will persist between tests
    delete navigator.clipboard;
  });
});
