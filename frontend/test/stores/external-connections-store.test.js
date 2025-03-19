import {
  expect,
  test,
  beforeEach,
  describe,
  beforeAll,
  afterAll,
  afterEach,
} from 'vitest';
import { useExternalConnectionsStore, createExternalConnectionsStore } from '@/stores/external-connections-store';
import { createPinia } from 'pinia';
import { setupServer } from 'msw/node';
import { HttpResponse, http } from 'msw';
import { createFetch } from '@vueuse/core';
import { ExternalConnectionProviders } from '@/definitions';
import withSetup from '../utils/with-setup';

const API_URL = 'http://localhost';

const restHandlers = [
  http.get(`${API_URL}/account/external-connections`, async () => HttpResponse.json({
    fxa: [{
      owner_id: 1,
      name: 'MozillaAccount1',
      type: 'fxa',
      type_id: 'f',
    }],
    google: [{
      owner_id: 1,
      name: 'GoogleAccount1',
      type: 'google',
      type_id: 'g',
    }],
    zoom: [{
      owner_id: 1,
      name: 'ZoomAccount1',
      type: 'zoom',
      type_id: 'z',
    }],
    caldav: [{
      owner_id: 1,
      name: 'CalDAVAccount1',
      type: 'caldav',
      type_id: 'c',
    }],
  })),
  http.get(`${API_URL}/zoom/auth`, async () => HttpResponse.json({
    url: 'https://example.org',
  })),
  http.get(`${API_URL}/'zoom/disconnect`, async () => true),
];

const server = setupServer(...restHandlers);

describe('External Connections Store', () => {
  let app = null;

  // Create a pinia instance before each test
  beforeEach(() => {
    app = withSetup();
    app.use(createPinia());
  });
  // Start server before all tests
  beforeAll(() => server.listen());

  // Close server after all tests
  afterAll(() => server.close());

  // Reset handlers after each test `important for test isolation`
  afterEach(() => {
    server.resetHandlers();
    app?.unmount();
  });

  test('init', () => {
    const ec = useExternalConnectionsStore();
    expect(ec.isLoaded).toBe(false);
    expect(ec.connections.fxa.length).toBe(0);
    expect(ec.connections.google.length).toBe(0);
    expect(ec.connections.zoom.length).toBe(0);
    expect(ec.connections.caldav.length).toBe(0);
  });

  test('fetch', async () => {
    const ec = createExternalConnectionsStore(createFetch({ baseUrl: API_URL }));
    await ec.fetch();
    expect(ec.isLoaded).toBe(true);
    expect(ec.connections.fxa.length).toBe(1);
    expect(ec.connections.fxa[0].owner_id).toBe(1);
    expect(ec.connections.fxa[0].name).toBe('MozillaAccount1');
    expect(ec.connections.fxa[0].type).toBe('fxa');
    expect(ec.connections.fxa[0].type_id).toBe('f');
    expect(ec.connections.google.length).toBe(1);
    expect(ec.connections.zoom.length).toBe(1);
    expect(ec.connections.caldav.length).toBe(1);
  });

  test('connect zoom', async () => {
    const ec = createExternalConnectionsStore(createFetch({ baseUrl: API_URL }));
    await ec.connect(ExternalConnectionProviders.Zoom);
    // TODO: expect location change
  });

  test('reset', async () => {
    const ec = createExternalConnectionsStore(createFetch({ baseUrl: API_URL }));
    await ec.fetch();

    // Check if appointments exist
    expect(ec.isLoaded).toBe(true);
    expect(ec.connections.fxa.length).toBe(1);
    expect(ec.connections.google.length).toBe(1);
    expect(ec.connections.zoom.length).toBe(1);
    expect(ec.connections.caldav.length).toBe(1);

    // Reset the appointment which should null all appointment data.
    ec.$reset();

    // Ensure our data is null/don't exist
    expect(ec.isLoaded).toBe(false);
    expect(ec.connections.fxa.length).toBe(0);
    expect(ec.connections.google.length).toBe(0);
    expect(ec.connections.zoom.length).toBe(0);
    expect(ec.connections.caldav.length).toBe(0);
  });
});
