import { UserManager, UserManagerSettings } from "oidc-client-ts";

const settings: UserManagerSettings = {
  authority: import.meta.env?.VITE_OIDC_ROOT_URL,
  client_id: import.meta.env?.VITE_OIDC_CLIENT_ID,
  redirect_uri: `${window.location.origin}/post-login/`
}

export const userManager = new UserManager(settings);
