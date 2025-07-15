import {AuthSchemes} from "@/definitions";

export const isOidcAuth = import.meta.env?.VITE_AUTH_SCHEME === AuthSchemes.Oidc;
export const isFxaAuth = import.meta.env?.VITE_AUTH_SCHEME === AuthSchemes.Fxa;
export const isPasswordAuth = import.meta.env?.VITE_AUTH_SCHEME === AuthSchemes.Password;
