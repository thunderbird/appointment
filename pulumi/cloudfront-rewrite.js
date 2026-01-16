  async function handler(event) {
    const request = event.request;
    const headers = request.headers;
    const host = headers.host.value;
    const apiPath = '/api/v1';
    const ignorePaths = [
      '/fxa',
      '/assets',
      '/sitemap.txt',
      '/favicon.ico',
      '/favicon-dark.ico',
      '/site.webmanifest',
      '/apple-touch-icon.png',
      '/android-chrome-192x192.png',
      '/android-chrome-512x512.png',
      '/favicon-16x16.png',
      '/favicon-32x32.png',
    ];
    const pathCheckFn = (path) => request.uri.startsWith(path);
    const domainRewrites = {
      'apt.mt': 'appointment.tb.pro',
      'stage.apt.mt': 'appointment-stage.tb.pro'
    }

    // If we got a short URL, rewrite to the long domain with '/user' prepended
    if (Object.keys(domainRewrites).includes(host)) {
      return {
        statusCode: 302,
        statusDescription: 'Found',
        headers: {
          location: {value: `https://${domainRewrites[host]}/user${request.uri}`}
        }
      }
    }

    // If our api path is the first thing that's found in the uri then remove it from the uri.
    if (request.uri.indexOf(apiPath) === 0) {
      request.uri = request.uri.replace(apiPath, '');
    } else if (!ignorePaths.some(pathCheckFn)) {
      // If we're not in one of the ignorePaths then force them to /index.html
      request.uri = '/index.html';
    }

    // If empty, then add a slash!
    // Required by AWS, see https://github.com/thunderbird/appointment/pull/510/
    if (request.uri === '') {
      request.uri = '/';
    }

    // else carry on like normal.
    return request;
  }
