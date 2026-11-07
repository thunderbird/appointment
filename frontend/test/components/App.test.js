import { afterAll, afterEach, beforeAll, expect, test, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia } from 'pinia';
import { setupServer } from 'msw/node';
import { HttpResponse, http } from 'msw';
import App from '@/App.vue';
import router from '@/router';
import i18ninstance from '@/composables/i18n';
import useDayJS from '@/composables/dayjs';
import { apiUrlKey } from '@/keys';
import { useUserStore } from '@/stores/user-store';
import { useCalendarStore } from '@/stores/calendar-store';
import withSetup from '../utils/with-setup';

const API_URL = 'http://localhost';

// The backend rejects the expired token and accepts the one issued at sign-in.
const server = setupServer(
  http.get(`${API_URL}/session-info`, () => HttpResponse.json(true)),
  http.post(`${API_URL}/token`, () => HttpResponse.json({ access_token: 'fresh', token_type: 'bearer' })),
  http.get(`${API_URL}/me`, () => HttpResponse.json({ email: 'owner@example.com', is_setup: true })),
  http.all(`${API_URL}/*`, ({ request }) => (request.headers.get('authorization') === 'Bearer expired'
    ? HttpResponse.json({ detail: { id: 'INVALID_TOKEN' } }, { status: 401 })
    : HttpResponse.json({}))),
);

beforeAll(() => server.listen());
afterAll(() => server.close());

let app;
let wrapper;
afterEach(() => {
  wrapper.unmount();
  app.unmount();
  window.localStorage.clear();
  window.sessionStorage.clear();
  server.resetHandlers();
});

test.each([1, 2])('signing in again after %i expired requests returns to the intended page', async (requestCount) => {
  const delayedResponse = Promise.withResolvers();
  server.use(http.get(`${API_URL}/me/calendars`, async ({ request }) => {
    if (request.headers.get('authorization') === 'Bearer expired') {
      await delayedResponse.promise;
      return HttpResponse.json({ detail: { id: 'INVALID_TOKEN' } }, { status: 401 });
    }
    return HttpResponse.json([]);
  }));

  const pinia = createPinia();
  app = withSetup().use(pinia);
  useUserStore().data.accessToken = 'expired';
  const confirmLink = '/user/owner/signature/confirm/1/token/1';
  await router.push(confirmLink);

  wrapper = mount(App, {
    global: {
      plugins: [pinia, router, i18ninstance, { install: (app) => useDayJS(app, 'en') }],
      provide: { [apiUrlKey]: API_URL },
    },
  });
  // A calendar request from the previous page finishes after the login redirect.
  const pendingRequest = requestCount === 2 ? useCalendarStore().fetch() : null;
  await vi.waitFor(() => expect(router.currentRoute.value.name).toBe('login'));
  delayedResponse.resolve();
  await pendingRequest;

  // The identity provider sends the user back here after sign-in.
  await router.push('/post-login/one-time-token');

  await vi.waitFor(() => expect(router.currentRoute.value.fullPath).toBe(confirmLink));
});
