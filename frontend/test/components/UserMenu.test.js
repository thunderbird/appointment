import { describe, it, expect, afterEach } from 'vitest';
import { mount } from '@vue/test-utils';
import i18ninstance from '@/composables/i18n';
import router from '@/router';
import { accountsTbProfileUrlKey, supportUrlKey } from '@/keys';
import UserMenu from '@/components/UserMenu.vue';

describe('UserMenu', () => {
  var wrapper;

  const getMountOptions = (provide = {}) => ({
    props: { username: 'fakeuser' },
    global: {
      plugins: [i18ninstance, router],
      provide,
    },
  });

  const openMenu = async () => {
    await wrapper.find('.avatar').trigger('click');
    return wrapper.find('.dropdown');
  };

  afterEach(() => {
    wrapper.unmount();
  });

  it('renders the manage subscription link pointing at the accounts origin', async () => {
    wrapper = mount(
      UserMenu,
      getMountOptions({
        [accountsTbProfileUrlKey]: 'https://accounts-stage.tb.pro/dashboard',
        [supportUrlKey]: 'https://support.example.com',
      }),
    );

    const dropdown = await openMenu();
    const link = dropdown.findAll('a').find((a) => a.text() === 'Manage subscription');
    expect(link, 'expected manage subscription link to be rendered').toBeDefined();
    expect(link.attributes('href')).toBe('https://accounts-stage.tb.pro/api/v1/subscription/paddle/portal/');
    expect(link.attributes('target')).toBe('_blank');
    expect(link.attributes('rel')).toBe('noopener');
  });

  it('hides the manage subscription link when no accounts url is provided', async () => {
    wrapper = mount(UserMenu, getMountOptions());

    const dropdown = await openMenu();
    expect(dropdown.text()).not.toContain('Manage subscription');
  });

  it('labels the logout item "Sign out"', async () => {
    wrapper = mount(UserMenu, getMountOptions());

    const dropdown = await openMenu();
    expect(dropdown.text()).toContain('Sign out');
    expect(dropdown.text()).not.toContain('Logout');
  });
});
