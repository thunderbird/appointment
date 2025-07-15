  async function handler(event) {
    const request = event.request;
    const apiPath = "/api/v1";
    const ignorePaths = ['/fxa', '/assets', '/appointment_logo.svg', '/sitemap.txt'];
    const pathCheckFn = (path) => request.uri.startsWith(path);

    // If our api path is the first thing that's found in the uri then remove it from the uri.
    if (request.uri.indexOf(apiPath) === 0) {
      request.uri = request.uri.replace(apiPath, "");
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
