import { defineStore } from 'pinia';
import { useLocalStorage } from '@vueuse/core';
import { i18n } from '@/composables/i18n';
import { computed, inject, watch, ref } from 'vue';
import {
  Subscriber, User, Fetch, Error, BooleanResponse, SignatureResponse, SubscriberResponse, TokenResponse,
  UserConfig,
} from '@/models';
import { usePosthog, posthog } from '@/composables/posthog';
import { dayjsKey } from '@/keys';
import { ColorSchemes } from '@/definitions';

const initialUserConfigObject = {
  language: null,
  colorScheme: null,
  timeFormat: null,
  timezone: null,
} as UserConfig;

const initialUserObject = {
  email: null,
  preferredEmail: null,
  level: null,
  name: null,
  settings: initialUserConfigObject,
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

  const call = ref(null);

  /**
   * Initialize store with data required at runtime
   * 
   * @param fetch preconfigured function to perform API calls
   */
  const init = (fetch: Fetch) => {
    call.value = fetch;
  }

  // Init user config if not already available
  if (!data.value?.settings) {
    const dj = inject(dayjsKey);
    const detectedTimeFormat = Number(dj('2022-05-24 20:00:00').format('LT').split(':')[0]) > 12 ? 24 : 12;    

    data.value.settings = {
      language: i18n.locale.value,
      colorScheme: ColorSchemes.System,
      timeFormat: detectedTimeFormat,
      timezone: dj.tz.guess(),
    };
  }

  /**
   * Update user settings only
   */
  const updateSettings = async () => {
    const obj = {
      username: data.value.username,
      language: data.value.settings.language,
      timezone: data.value.settings.timezone,
      color_scheme: data.value.settings.colorScheme,
      time_mode: data.value.settings.timeFormat,
    };

    const { error }: SubscriberResponse = await call.value('me').put(obj).json();
    if (!error.value) {
      // TODO show some confirmation
    } else {
      // TODO show error message
    }
  };

  /**
   * Return the first schedule link or their signed url
   */
  const myLink = computed((): string => {
    const scheduleLinks = data?.value?.scheduleLinks ?? [];
    if (scheduleLinks.length > 0) {
      return scheduleLinks[0];
    }

    // TODO: Signed urls are deprecated here!
    return data.value.signedUrl;
  });

  /**
   * Return the last unique URL part of the users link
   */
  const mySlug = computed((): string => {
    const link = myLink?.value?.replace(/\/+$/, '');
    return link?.slice(link.lastIndexOf('/') + 1);
  });

  /**
   * Return the user color scheme
   */
  const myColorScheme = computed((): ColorSchemes => {
    switch (data.value.settings.colorScheme) {
      case 'dark':
        return ColorSchemes.Dark;
      case 'light':
        return ColorSchemes.Light;
      case 'system':
      default:
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? ColorSchemes.Dark : ColorSchemes.Light;
    }
  });

  /**
   * True if user has a valid access token
   */
  const authenticated = computed((): boolean => data.value.accessToken !== null);

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
      settings: {
        language: subscriber.language,
        colorScheme: subscriber.color_scheme,
        timeFormat: subscriber.time_mode,
        timezone: subscriber.timezone,
      },
      avatarUrl: subscriber.avatar_url,
      isSetup: subscriber.is_setup,
      scheduleLinks: subscriber.schedule_links,
      uniqueHash: subscriber.unique_hash,
    };
  };

  /**
   * Retrieve the current signed url and update store
   */
  const updateSignedUrl = async (): Promise<Error> => {
    const { error, data: sigData }: SignatureResponse = await call.value('me/signature').get().json();

    if (error.value || !sigData.value?.url) {
      return { error: sigData.value ?? error.value };
    }

    data.value.signedUrl = sigData.value.url;

    return { error: false };
  };

  /**
   * Retrieve the current signed url and update store
   * @param inputData Subscriber data to throw into the db
   */
  const updateUser = async (inputData: Subscriber) => {
    const { error, data: userData }: SubscriberResponse = await call.value('me').put(inputData).json();
  
    if (!error.value) {
      // update user in store
      updateProfile(userData.value);
      await updateSignedUrl();

      return { error: false };
    }

    return { error: data.value ?? error.value };
  };

  /**
   * Retrieve the current signed url and update store
   */
  const finishFTUE = async () => call.value('subscriber/setup').post().json();

  /**
   * Update store with profile data from db
   */
  const profile = async (): Promise<Error> => {
    const { error, data: userData }: SubscriberResponse = await call.value('me').get().json();

    // Type error means they refreshed midway through the request. Don't log them out for this!
    if (error.value instanceof TypeError) {
      return { error: error.value as unknown as string };
    }

    // Failed to get profile data, log this user out and return false
    if (error.value || !userData.value) {
      $reset();
      return { error: userData.value ?? error.value };
    }

    updateProfile(userData.value);

    return updateSignedUrl();
  };

  /**
   * Invalidate the current signed url and replace it with a new one
   */
  const changeSignedUrl = async (): Promise<Error> => {
    const { error, data: sigData }: BooleanResponse = await call.value('me/signature').post().json();

    if (error.value) {
      return { error: sigData.value ?? error.value };
    }

    return updateSignedUrl();
  };

  /**
   * Request subscriber login
   * @param username
   * @param password or null if fxa authentication
   */
  const login = async (username: string, password: string|null): Promise<Error> => {
    $reset();

    if (import.meta.env.VITE_AUTH_SCHEME === 'password') {
      // fastapi wants us to send this as formdata :|
      const formData = new FormData(document.createElement('form'));
      formData.set('username', username);
      formData.set('password', password);
      const { error, data: tokenData }: TokenResponse = await call.value('token').post(formData).json();

      if (error.value || !tokenData.value.access_token) {
        return { error: tokenData.value ?? error.value };
      }

      data.value.accessToken = tokenData.value.access_token;
    } else if (import.meta.env.VITE_AUTH_SCHEME === 'fxa') {
      // We get a one-time token back from the api, use it to fetch the real access token
      data.value.accessToken = username;
      const { error, data: tokenData }: TokenResponse = await call.value('fxa-token').post().json();

      if (error.value || !tokenData.value.access_token) {
        return { error: tokenData.value ?? error.value };
      }

      data.value.accessToken = tokenData.value.access_token;
    } else {
      return { error: i18n.t('error.loginMethodNotSupported') };
    }

    return profile();
  };

  /**
   * Do subscriber logout and reset store
   */
  const logout = async () => {
    const { error }: BooleanResponse = await call.value('logout').get().json();

    if (error.value) {
      // TODO: show error message
      console.warn('Error logging out: ', error.value);
    }

    $reset();
  };

  // Make sure settings are saved directly when changed
  watch(
    () => data.value.settings,
    () => {
      if (authenticated.value) {
        updateSettings();
      }
    },
    { deep: true }
  );

  return {
    data,
    init,
    authenticated,
    $reset,
    updateSignedUrl,
    profile,
    updateProfile,
    changeSignedUrl,
    login,
    logout,
    myLink,
    mySlug,
    myColorScheme,
    updateUser,
    finishFTUE,
  };
});
