import { defineStore } from 'pinia';
import { useLocalStorage } from '@vueuse/core';
import { i18n } from '@/composables/i18n';
import { computed, inject } from 'vue';
import {
  Subscriber, User, Fetch, Error, BooleanResponse, SignatureResponse, SubscriberResponse, TokenResponse,
} from '@/models';
import { usePosthog, posthog } from '@/composables/posthog';

const initialUserObject = {
  email: null,
  preferredEmail: null,
  level: null,
  name: null,
  timezone: null,
  username: null,
  signedUrl: null,
  avatarUrl: null,
  accessToken: null,
  scheduleLinks: [],
  isSetup: false,
  uniqueHash: null,
} as User;

export const useUserStore = defineStore('user', () => {
  const data = useLocalStorage('tba/user', structuredClone(initialUserObject));

  /**
   * Return the first schedule link or their signed url
   */
  const myLink = computed((): string => {
    const scheduleLinks = data?.value?.scheduleLinks ?? [];
    if (scheduleLinks.length > 0) {
      return scheduleLinks[0];
    }

    console.warn('Signed urls are deprecated here!');
    return data.value.signedUrl;
  });


  const authenticated = computed((): boolean => {
    return data.value.accessToken !== null;
  });
  /**
   * @deprecated - Use authenticated
   * @see this.authenticated
   */
  const exists = () => data.value.accessToken !== null;
  const $reset = () => {
    if (usePosthog) {
      posthog.reset();
    }
    data.value = structuredClone(initialUserObject);
  };

  const updateProfile = (subscriber: Subscriber) => {
    data.value = {
      // Include the previous values first
      ...data.value,
      // Then the new ones!
      username: subscriber.username,
      name: subscriber.name,
      email: subscriber.email,
      preferredEmail: subscriber?.preferred_email ?? subscriber.email,
      level: subscriber.level,
      timezone: subscriber.timezone,
      avatarUrl: subscriber.avatar_url,
      isSetup: subscriber.is_setup,
      scheduleLinks: subscriber.schedule_links,
      uniqueHash: subscriber.unique_hash,
    };
  };

  /**
   * Retrieve the current signed url and update store
   * @param call preconfigured API fetch function
   */
  const updateSignedUrl = async (call: Fetch): Promise<Error> => {
    const { error, data: sigData }: SignatureResponse = await call('me/signature').get().json();

    if (error.value || !sigData.value?.url) {
      return { error: sigData.value ?? error.value };
    }

    data.value.signedUrl = sigData.value.url;

    return { error: false };
  };

  const updateUser = async (fetch, inputData) => {
    const { data: userData, error } = await fetch('me').put(inputData).json();
    if (!error.value) {
      // update user in store
      updateProfile(userData.value);
      await updateSignedUrl(fetch);

      return { error: false };
    }

    return { error: data.value ?? error.value };
  };

  const finishFTUE = async (fetch) => fetch('subscriber/setup').post().json();

  /**
   * Update store with profile data from db
   * @param call preconfigured API fetch function
   */
  const profile = async (call: Fetch): Promise<Error> => {
    const { error, data: userData }: SubscriberResponse = await call('me').get().json();

    // Failed to get profile data, log this user out and return false
    if (error.value || !userData.value) {
      $reset();
      return { error: userData.value ?? error.value };
    }

    updateProfile(userData.value);

    return updateSignedUrl(call);
  };

  /**
   * Invalidate the current signed url and replace it with a new one
   * @param call preconfigured API fetch function
   */
  const changeSignedUrl = async (call: Fetch): Promise<Error> => {
    const { error, data: sigData }: BooleanResponse = await call('me/signature').post().json();

    if (error.value) {
      return { error: sigData.value ?? error.value };
    }

    return updateSignedUrl(call);
  };

  /**
   * Request subscriber login
   * @param call preconfigured API fetch function
   * @param username
   * @param password or null if fxa authentication
   */
  const login = async (call: Fetch, username: string, password: string|null): Promise<Error> => {
    $reset();

    if (import.meta.env.VITE_AUTH_SCHEME === 'password') {
      // fastapi wants us to send this as formdata :|
      const formData = new FormData(document.createElement('form'));
      formData.set('username', username);
      formData.set('password', password);
      const { error, data: tokenData }: TokenResponse = await call('token').post(formData).json();

      if (error.value || !tokenData.value.access_token) {
        return { error: tokenData.value ?? error.value };
      }

      data.value.accessToken = tokenData.value.access_token;
    } else if (import.meta.env.VITE_AUTH_SCHEME === 'fxa') {
      // We get a one-time token back from the api, use it to fetch the real access token
      data.value.accessToken = username;
      const { error, data: tokenData }: TokenResponse = await call('fxa-token').post().json();

      if (error.value || !tokenData.value.access_token) {
        return { error: tokenData.value ?? error.value };
      }

      data.value.accessToken = tokenData.value.access_token;
    } else {
      return { error: i18n.t('error.loginMethodNotSupported') };
    }

    return profile(call);
  };

  /**
   * Do subscriber logout and reset store
   * @param call preconfigured API fetch function
   */
  const logout = async (call: Fetch) => {
    const { error }: BooleanResponse = await call('logout').get().json();

    if (error.value) {
      // TODO: show error message
      console.warn('Error logging out: ', error.value);
    }

    $reset();
  };

  return {
    data,
    authenticated,
    exists,
    $reset,
    updateSignedUrl,
    profile,
    updateProfile,
    changeSignedUrl,
    login,
    logout,
    myLink,
    updateUser,
    finishFTUE,
  };
});
