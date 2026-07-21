import { UserManager, UserManagerSettings } from 'oidc-client-ts';
import { config } from '@/config';

const settings: UserManagerSettings = {
  authority: config.oidcRootUrl,
  client_id: config.oidcClientId,
  redirect_uri: `${window.location.origin}/post-login/`,
};

export const userManager = new UserManager(settings);
