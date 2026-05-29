async function handler(event) {
  const request = event.request;
  const headers = request.headers;
  const host = headers.host.value;
  const apiPath = "/api/v1";
  const ignorePaths = [
    "/fxa",
    "/assets",
    "/sitemap.txt",
    "/favicon.svg",
    "/site.webmanifest",
    "/apple-touch-icon.png",
    "/android-chrome-192x192.png",
    "/android-chrome-512x512.png",
    "/favicon-16x16.png",
    "/favicon-32x32.png",
  ];
  const pathCheckFn = (path) => request.uri.startsWith(path);
  const domainRewrites = {
    "apt.mt": "appointment.tb.pro",
    "stage.apt.mt": "appointment-stage.tb.pro",
  };

  // Rebuild the request's query string into a redirectable string. CloudFront Functions
  // expose request.querystring as an object (not a string), so we serialize it ourselves
  // and preserve raw values (they arrive already URL-encoded). Returns '' when empty.
  const buildQueryString = (querystring) => {
    const params = [];
    Object.keys(querystring).forEach((key) => {
      const param = querystring[key];
      if (param.multiValue) {
        param.multiValue.forEach((entry) =>
          params.push(`${key}=${entry.value}`),
        );
      } else {
        params.push(`${key}=${param.value}`);
      }
    });
    return params.length ? `?${params.join("&")}` : "";
  };

  // Short URLs omit /user/; prepend it when redirecting booking paths to the long domain.
  // Root requests (apt.mt/) should land on the main site home, not /user/.
  if (Object.keys(domainRewrites).includes(host)) {
    const longHost = domainRewrites[host];
    const queryString = buildQueryString(request.querystring);
    const path =
      request.uri === "/" || request.uri === "" ? "/" : `/user${request.uri}`;
    const location = `https://${longHost}${path}${queryString}`;

    return {
      statusCode: 302,
      statusDescription: "Found",
      headers: {
        location: { value: location },
      },
    };
  }

  // If our api path is the first thing that's found in the uri then remove it from the uri.
  if (request.uri.indexOf(apiPath) === 0) {
    request.uri = request.uri.replace(apiPath, "");
  } else if (!ignorePaths.some(pathCheckFn)) {
    // If we're not in one of the ignorePaths then force them to /index.html
    request.uri = "/index.html";
  }

  // If empty, then add a slash!
  // Required by AWS, see https://github.com/thunderbird/appointment/pull/510/
  if (request.uri === "") {
    request.uri = "/";
  }

  // else carry on like normal.
  return request;
}
