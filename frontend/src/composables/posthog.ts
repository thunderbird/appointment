 
import { default as ph } from 'posthog-js';

/**
 * Can we use posthog?
 */
export const usePosthog = !!import.meta.env.VITE_POSTHOG_PROJECT_KEY;

/**
 * PostHog instance, please gate all calls with usePosthog
 * @see usePosthog
 */
export const posthog = ph;
