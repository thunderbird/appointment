import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing';
import i18ninstance from '@/composables/i18n';
import router from '@/router';
import withSetup from '../utils/with-setup';
import { useUserStore } from '@/stores/user-store';
import { RouterLink } from 'vue-router';
import FooterBar from '@/components/FooterBar.vue';


describe('FooterBar', () => {
  var app;
  var wrapper;

  // create a pinia instance the FooterBar uses the UserStore
  beforeEach(() => {
    app = withSetup();
    app.use(createTestingPinia());
  });

  afterEach(() => {
    wrapper.unmount();
  });

  it('renders correctly when not logged in', () => {
    wrapper = mount(FooterBar, {
      global: {
        // the FooterBar uses i18n and rounter-link so install these global component plugins
        plugins: [i18ninstance, router],
      },
    });

    // verify all expected router-link child components were rendered
    const expectedLinks = ['/privacy', '/terms'];
    const allRouterLinks = wrapper.findAllComponents(RouterLink);
    var foundLinks = [];
    for (let link of allRouterLinks) {
      foundLinks.push(link.props().to);
    }
    expect(foundLinks.length).toBe(expectedLinks.length);
    for (let expLink of expectedLinks) {
      expect(foundLinks, 'expected link component to be rendered').toContain(expLink);
    }

    // verify we show the external Thunderbird Pro link and no support link
    const proLink = wrapper.find(`a[href="${import.meta.env.VITE_TB_PRO_URL}"]`);
    expect(proLink.exists()).toBe(true);
    expect(proLink.text()).toBe(i18ninstance.global.t('label.exploreThunderbirdPro'));
    expect(wrapper.find('.contact-support-link').exists()).toBe(false);
  });

  it('renders correctly when logged in', () => {
    // fake sign-in via user store
    const user = useUserStore();
    user.data.accessToken = 'abc';
    expect(user.authenticated).toBe(true);

    wrapper = mount(FooterBar, {
      global: {
        // the FooterBar uses i18n and rounter-link so install these global component plugins
        plugins: [i18ninstance, router],
      },
    }); 

    // verify all expected router-link child components were rendered
    const expectedLinks = ['dashboard', 'bookings', 'availability', 'settings', '/privacy', '/terms'];
    const allRouterLinks = wrapper.findAllComponents(RouterLink);
    var foundLinks = [];
    for (let link of allRouterLinks) {
      foundLinks.push(link.props().to);
    }
    expect(foundLinks.length).toBe(expectedLinks.length);
    for (let expLink of expectedLinks) {
      expect(foundLinks, 'expected link component to be rendered').toContain(expLink);
    }

    // verify the support link is rendered for authenticated users
    const supportLink = wrapper.find('.contact-support-link');
    expect(supportLink.exists()).toBe(true);
    expect(supportLink.attributes('href')).toBe(import.meta.env.VITE_SUPPORT_URL);
    expect(supportLink.text()).toBe(i18ninstance.global.t('label.needHelpVisitSupport'));
  });
});
