import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import i18ninstance from '@/composables/i18n';
import router from '@/router';
import withSetup from '../utils/with-setup';
import { useUserStore } from '@/stores/user-store';
import { RouterLink } from 'vue-router';
import FooterBar from '@/components/FooterBar.vue';
import { supportUrlKey, tbProUrlKey } from '@/keys';
import { STATUS_PAGE_URL, IDEAS_PAGE_URL } from '@/definitions';

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
        provide: {
          [tbProUrlKey]: import.meta.env.VITE_TB_PRO_URL,
        },
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

    // verify we show only the external Thundermail link for unauthenticated users
    const proLink = wrapper.find(`a[href="${import.meta.env.VITE_TB_PRO_URL}"]`);
    expect(proLink.exists()).toBe(true);
    expect(proLink.text()).toBe(i18ninstance.global.t('label.exploreThundermail'));

    // the status, support and ideas links are only shown to authenticated users
    expect(wrapper.find('.default-links').exists()).toBe(false);
    expect(wrapper.find(`a[href="${STATUS_PAGE_URL}"]`).exists()).toBe(false);
    expect(wrapper.find(`a[href="${IDEAS_PAGE_URL}"]`).exists()).toBe(false);
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
        provide: {
          [supportUrlKey]: import.meta.env.VITE_SUPPORT_URL,
        },
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

    // verify the status, support and ideas links are rendered for authenticated users
    const statusLink = wrapper.find(`a[href="${STATUS_PAGE_URL}"]`);
    expect(statusLink.exists()).toBe(true);
    expect(statusLink.text()).toBe(i18ninstance.global.t('label.status'));

    const supportLink = wrapper.find(`a[href="${import.meta.env.VITE_SUPPORT_URL}"]`);
    expect(supportLink.exists()).toBe(true);
    expect(supportLink.text()).toBe(i18ninstance.global.t('label.needHelpVisitSupport'));

    const ideasLink = wrapper.find(`a[href="${IDEAS_PAGE_URL}"]`);
    expect(ideasLink.exists()).toBe(true);
    expect(ideasLink.text()).toBe(i18ninstance.global.t('label.ideas'));
  });
});
