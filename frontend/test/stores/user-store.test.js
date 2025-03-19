import {
  expect,
  test,
  beforeEach,
  describe,
  beforeAll,
  afterAll,
  afterEach,
} from 'vitest';
import { useUserStore, createUserStore } from '@/stores/user-store';
import { createPinia, setActivePinia } from 'pinia';
import { setupServer } from 'msw/node';
import { HttpResponse, http } from 'msw';
import { createFetch } from '@vueuse/core';

const API_URL = 'http://localhost';
const TEST_USERNAME = 'test';
const TEST_PASSWORD = 'password';

const beforeFetch = async (options, user) => {
  if (user.authenticated) {
    const token = await user.data.accessToken;
    options.headers.Authorization = `Bearer ${token}`;
  }
  return { options };
};

const restHandlers = [
  http.post(`${API_URL}/token`, async ({ request }) => {
    const formData = await request.formData();

    // Send mock error if the username/password don't match our test username/password
    if (formData.get('username') !== TEST_USERNAME || formData.get('password') !== TEST_PASSWORD) {
      return HttpResponse.json({
        detail: 'User credentials mismatch',
      }, { status: 403 });
    }

    return HttpResponse.json({
      access_token: 'You have access!',
    });
  }),
  http.get(`${API_URL}/me`, async (request) => {
    const headers = await request.request.headers;

    // Fail without an access token
    if (!headers.get('authorization')) {
      return HttpResponse.json({
        detail: 'Not authenticated',
      }, { status: 403 });
    }

    return HttpResponse.json({
      username: TEST_USERNAME,
      name: 'Test',
      email: 'test@example.org',
      level: 1,
      timezone: 'America/Vancouver',
      language: 'de',
      time_mode: 12,
      colour_scheme: 'dark',
      avatar_url: null,
    });
  }),
  http.get(`${API_URL}/me/signature`, async (request) => {
    const headers = await request.request.headers;

    // Fail without an access token
    if (!headers.get('authorization')) {
      return HttpResponse.json({
        detail: 'Not authenticated',
      }, { status: 403 });
    }

    return HttpResponse.json({
      url: 'https://blah',
    });
  }),
];

const server = setupServer(...restHandlers);
/* server.events.on('request:start', ({ request }) => {
  console.log('Outgoing:', request.method, request.url);
}); */

describe('User Store', () => {
  // Create a pinia instance before each test
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  // Start server before all tests
  beforeAll(() => server.listen());

  //  Close server after all tests
  afterAll(() => server.close());

  // Reset handlers after each test `important for test isolation`
  afterEach(() => server.resetHandlers());

  test('exists', () => {
    const user = useUserStore();
    user.data.accessToken = 'abc';
    expect(user.authenticated).toBe(true);
  });

  test('does not exist', () => {
    const user = useUserStore();
    user.$reset();
    expect(user.authenticated).toBe(false);
  });

  test('reset', () => {
    const user = useUserStore();

    // Add some data to the user store
    user.$patch({
      data: {
        email: 'test@example.org',
        name: 'test',
        accessToken: 'abc',
      },
    });

    // Check if the user exists (because we have an access token)
    expect(user.authenticated === true);

    // Reset the user which should null all user data.
    user.$reset();

    // Ensure our data is null/don't exist
    expect(user.authenticated).toBe(false);
    expect(user.data.name).toBeNull();
    expect(user.data.email).toBeNull();
    expect(user.data.signedUrl).toBeNull();
  });

  test('login fails', async () => {
    const user = createUserStore(createFetch({
      baseUrl: API_URL,
    }));

    const response = await user.login(TEST_USERNAME, `${TEST_PASSWORD}_thispasswordisnolongerokay`);
    expect(response === false);
  });

  test('login successful', async () => {
    // This will call profile() as well!
    const user = createUserStore(createFetch({
      baseUrl: API_URL,
      options: {
        beforeFetch: async ({ options }) => beforeFetch(options, user),
      },
    }));

    const response = await user.login(TEST_USERNAME, `${TEST_PASSWORD}`);

    expect(response.error).toBe(false);
    expect(user.authenticated).toBe(true);
    expect(user.data.accessToken).toBeTruthy();
    expect(user.data.username).toBeTruthy();
    expect(user.data.email).toBeTruthy();
    expect(user.data.name).toBeTruthy();
    expect(user.data.level).toBeTruthy();
    expect(user.data.settings.timezone).toBeTruthy();
    expect(user.data.settings.language).toBeTruthy();
    expect(user.data.settings.timeFormat).toBeTruthy();
    expect(user.data.settings.colourScheme).toBeTruthy();
    expect(user.data.signedUrl).toBeTruthy();
  });
});
