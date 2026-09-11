import { useDark } from '@vueuse/core';

/**
 * Reactive dark mode state. Defaults to the user-agent / device colour scheme
 * preference, but can be overridden by the user via toggleColourScheme();
 * the override is then persisted (see STORAGE_KEY) and takes precedence over
 * the device preference until toggled again.
 */
export const STORAGE_KEY = 'tba/colour-scheme';

export const isDark = useDark({
  storageKey: STORAGE_KEY,
});

export const toggleColourScheme = () => {
  isDark.value = !isDark.value;
};
