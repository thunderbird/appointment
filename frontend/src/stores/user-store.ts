import { defineStore } from 'pinia';
import { useLocalStorage } from '@vueuse/core';
import { i18n } from '@/composables/i18n';
import { computed } from 'vue';
import { Schedule, Subscriber, User, FetchAny, FetchBoolean, Error } from '@/models';

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
  scheduleSlugs: [],
} as User;

export const useUserStore = defineStore('user', () => {
  const data = useLocalStorage('tba/user', structuredClone(initialUserObject));

  const myLink = computed((): string => {
    const scheduleSlug = data.value?.scheduleSlugs?.length > 0 ? data.value?.scheduleSlugs[0] : null;
    if (scheduleSlug) {
      return `${import.meta.env.VITE_SHORT_BASE_URL}/${data.value.username}/${scheduleSlug}/`;
    }
    return data.value.signedUrl;
  });

  const exists = () => data.value.accessToken !== null;
  const $reset = () => {
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
    };
  };

  const updateScheduleUrls = (scheduleData: Schedule[]) => {
    data.value = {
      ...data.value,
      scheduleSlugs: scheduleData.map((schedule) => schedule?.slug),
    };
  };

  /**
   * Retrieve the current signed url and update store
   * @param {FetchSignature} call preconfigured API fetch function
   */
  const updateSignedUrl = async (call: FetchAny): Promise<Error> => {
    const { error, data: sigData } = await call('me/signature').get().json();

    if (error.value || !sigData.value?.url) {
      return { error: sigData.value?.detail ?? error.value };
    }

    data.value.signedUrl = sigData.value.url;

    return { error: false };
  };

  /**
   * Update store with profile data from db
   * @param {FetchSubscriber} call preconfigured API fetch function
   */
  const profile = async (call: FetchAny): Promise<Error> => {
    const { error, data: userData } = await call('me').get().json();

    // Failed to get profile data, log this user out and return false
    if (error.value || !userData.value) {
      $reset();
      return { error: userData.value?.detail ?? error.value };
    }

    updateProfile(userData.value);

    return updateSignedUrl(call);
  };

  /**
   * Invalidate the current signed url and replace it with a new one
   * @param call preconfigured API fetch function
   */
  const changeSignedUrl = async (call: FetchBoolean): Promise<Error> => {
    const { error, data: sigData } = await call('me/signature').post().json();

    if (error.value) {
      return { error: sigData.value ?? error.value };
    }

    return updateSignedUrl(call);
  };

  /**
   * Request subscriber login
   * @param {FetchToken} call preconfigured API fetch function
   * @param username
   * @param password or null if fxa authentication
   */
  const login = async (call: FetchAny, username: string, password: string|null): Promise<Error> => {
    $reset();

    if (import.meta.env.VITE_AUTH_SCHEME === 'password') {
      // fastapi wants us to send this as formdata :|
      const formData = new FormData(document.createElement('form'));
      formData.set('username', username);
      formData.set('password', password);
      const { error, data: tokenData } = await call('token').post(formData).json();

      if (error.value || !tokenData.value.access_token) {
        return { error: tokenData.value?.detail ?? error.value };
      }

      data.value.accessToken = tokenData.value.access_token;
    } else if (import.meta.env.VITE_AUTH_SCHEME === 'fxa') {
      // For FXA we re-use the username parameter as our access token
      data.value.accessToken = username;
    } else {
      return { error: i18n.t('error.loginMethodNotSupported') };
    }

    return profile(call);
  };

  /**
   * Do subscriber logout and reset store
   * @param call preconfigured API fetch function
   */
  const logout = async (call: FetchBoolean) => {
    const { error } = await call('logout').get().json();

    if (error.value) {
      // TODO: show error message
      console.warn('Error logging out: ', error.value);
    }

    $reset();
  };

  return {
    data, exists, $reset, updateSignedUrl, profile, updateProfile, changeSignedUrl, login, logout, myLink, updateScheduleUrls,
  };
});
