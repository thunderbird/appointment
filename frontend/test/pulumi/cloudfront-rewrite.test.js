import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { cwd } from 'node:process';

// The CloudFront Function is deployed by reading this file verbatim (see pulumi/cloudfront.py),
// so it must stay a bare `async function handler(event) {...}` with no import/export. We can't
// import it; instead we load the source and materialize `handler` via `new Function`.
//
// Caveat: this runs on Node's engine, NOT the cloudfront-js-2.0 runtime, so it verifies the
// redirect/serialization logic against AWS's documented event contract — not runtime parsing.
// Definitive runtime validation needs `aws cloudfront test-function`.
// vitest runs from frontend/ (its `test` script lives in frontend/package.json), so the
// CloudFront Function source sits one directory up under pulumi/.
const source = readFileSync(resolve(cwd(), '../pulumi/cloudfront-rewrite.js'), 'utf8');
const handler = new Function(`${source}\nreturn handler;`)();

// Build a fresh event per call (the handler mutates request.uri in place on the passthrough path).
const makeEvent = (host, uri, querystring = {}) => ({
  request: {
    method: 'GET',
    uri,
    querystring,
    headers: { host: { value: host } },
  },
});

const locationOf = async (event) => {
  const res = await handler(event);
  return res?.headers?.location?.value ?? null;
};

describe('cloudfront-rewrite handler — short-domain redirects', () => {
  it('redirects the root path to the long-domain home, not /user/', async () => {
    const res = await handler(makeEvent('apt.mt', '/'));
    expect(res.statusCode).toBe(302);
    expect(res.statusDescription).toBe('Found');
    expect(res.headers.location.value).toBe('https://appointment.tb.pro/');
  });

  it('treats an empty uri as root', async () => {
    expect(await locationOf(makeEvent('apt.mt', ''))).toBe('https://appointment.tb.pro/');
  });

  it('prepends /user to a short booking link', async () => {
    expect(await locationOf(makeEvent('apt.mt', '/john'))).toBe('https://appointment.tb.pro/user/john');
  });

  it('maps the stage short domain to the stage long domain', async () => {
    expect(await locationOf(makeEvent('stage.apt.mt', '/jane'))).toBe('https://appointment-stage.tb.pro/user/jane');
  });

  describe('query string preservation', () => {
    it('keeps a single query param', async () => {
      expect(await locationOf(makeEvent('apt.mt', '/john', { month: { value: '2026-06' } })))
        .toBe('https://appointment.tb.pro/user/john?month=2026-06');
    });

    it('keeps multiple query params in order', async () => {
      expect(await locationOf(makeEvent('apt.mt', '/john', { a: { value: '1' }, b: { value: '2' } })))
        .toBe('https://appointment.tb.pro/user/john?a=1&b=2');
    });

    it('keeps a valueless param as key= (AWS NoValue shape)', async () => {
      expect(await locationOf(makeEvent('apt.mt', '/john', { NoValue: { value: '' } })))
        .toBe('https://appointment.tb.pro/user/john?NoValue=');
    });

    it('expands a multiValue param into repeated keys', async () => {
      expect(await locationOf(makeEvent('apt.mt', '/john', {
        tag: { value: 'x', multiValue: [{ value: 'x' }, { value: 'y' }] },
      }))).toBe('https://appointment.tb.pro/user/john?tag=x&tag=y');
    });

    it('preserves already-encoded values without double-encoding', async () => {
      expect(await locationOf(makeEvent('apt.mt', '/john', { q: { value: 'a%20b' } })))
        .toBe('https://appointment.tb.pro/user/john?q=a%20b');
    });

    it('carries the query string through on the root redirect', async () => {
      expect(await locationOf(makeEvent('apt.mt', '/', { ref: { value: 'newsletter' } })))
        .toBe('https://appointment.tb.pro/?ref=newsletter');
    });
  });
});

describe('cloudfront-rewrite handler — non-rewrite hosts pass through', () => {
  it('does not redirect a long-domain request and rewrites SPA paths to /index.html', async () => {
    const res = await handler(makeEvent('appointment.tb.pro', '/dashboard'));
    expect(res.statusCode).toBeUndefined();
    expect(res.uri).toBe('/index.html');
  });

  it('strips the /api/v1 prefix from API requests', async () => {
    const res = await handler(makeEvent('appointment.tb.pro', '/api/v1/me'));
    expect(res.uri).toBe('/me');
  });
});
