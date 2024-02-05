// Polyfill to fix use/createFetch...
// Reference: https://github.com/reduxjs/redux-toolkit/issues/3254#issuecomment-1587624955
import nodeFetch, { Request, Response } from 'node-fetch';

Object.assign(global, { fetch: nodeFetch, Request, Response });
