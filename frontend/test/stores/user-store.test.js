import {
  expect,
  test,
  beforeEach,
  describe,
  beforeAll,
  afterAll,
  afterEach,
} from 'vitest';
import { useUserStore } from '@/stores/user-store';
import { createPinia, setActivePinia } from 'pinia';
import { setupServer } from 'msw/node';
import { HttpResponse, http } from 'msw';
import { createFetch } from '@vueuse/core';

const API_URL = 'http://localhost';
const TEST_USERNAME = 'test';
const TEST_PASSWORD = 'password';

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
      accessToken: 'You have access!',
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
      avatarUrl: null,
    });
  }),
];

const server = setupServer(...restHandlers);
server.events.on('request:start', ({ request }) => {
  // console.log('Outgoing:', request.method, request.url);
});

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
    expect(user.exists() === true);
  });
  test('does not exist', () => {
    const user = useUserStore();
    expect(user.exists() === false);
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
    expect(user.exists() === true);

    // Reset the user which should null all user data.
    user.reset();

    // Ensure our data is null/don't exist
    expect(user.exists() === false);
    expect(user.data.name === null);
    expect(user.data.email === null);
  });
  test('login fails', async () => {
    const user = useUserStore();

    const response = await user.login(createFetch({
      baseUrl: API_URL,
    }), TEST_USERNAME, `${TEST_PASSWORD}_thispasswordisnolongerokay`);
    expect(response === false);
  });
  test('login successful', async () => {
    // This will call profile() as well!
    const user = useUserStore();

    const response = await user.login(createFetch({
      baseUrl: API_URL,
    }), TEST_USERNAME, `${TEST_PASSWORD}`);

    expect(response === true);
    expect(user.exists());
    expect(user.data.accessToken);
    expect(user.data.username);
    expect(user.data.email);
    expect(user.data.name);
    expect(user.data.level);
    expect(user.data.timezone);
  });
});
