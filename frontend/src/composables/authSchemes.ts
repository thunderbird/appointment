import { AuthSchemes } from '@/definitions';
import { config } from '@/config';

export const isOidcAuth = config.authScheme === AuthSchemes.Oidc;
export const isPasswordAuth = config.authScheme === AuthSchemes.Password;
