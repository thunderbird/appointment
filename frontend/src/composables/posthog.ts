import { default as ph } from 'posthog-js';
import { config } from '@/config';

/**
 * Can we use posthog?
 */
export const usePosthog = !!config.posthogProjectKey;

/**
 * PostHog instance, please gate all calls with usePosthog
 * @see usePosthog
 */
export const posthog = ph;
