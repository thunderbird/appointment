import { ConfigType, Dayjs, DayjsTimezone } from 'dayjs';
import { InjectionKey } from 'vue';
import { Fetch, Refresh } from '@/models';

/**
 * These are typed Symbols for use with inject/provide in VueJS
 */

// Provides Dayjs class functionality as well as the timezone plugin
type DayjsType = ((_?:ConfigType) => Dayjs) & {
  tz: DayjsTimezone
};
export const dayjsKey = Symbol('dayjs') as InjectionKey<DayjsType>;

// Provide urls for API and booking
export const apiUrlKey = Symbol('apiUrl') as InjectionKey<string>;
export const bookingUrlKey = Symbol('bookingUrl') as InjectionKey<string>;

// Provide environment and authentication keys
export const isPasswordAuthKey = Symbol('isPasswordAuth') as InjectionKey<boolean>;
export const isFxaAuthKey = Symbol('isFxaAuth') as InjectionKey<boolean>;
export const fxaEditProfileUrlKey = Symbol('fxaEditProfileUrl') as InjectionKey<string>;

// Provides configured fetch call to our backend API
export const callKey = Symbol('call') as InjectionKey<Fetch>;

// Provides a freresh data function
export const refreshKey = Symbol('refresh') as InjectionKey<Refresh>;

// Provides functionality to paint background of event objects
type PaintBackgroundType = (element: Event, hexColor: string, hexTransparency?: string, reset?: boolean) => void;
export const paintBackgroundKey = Symbol('paintBackground') as InjectionKey<PaintBackgroundType>;

// Provides duration data in human friendly form
type DurationHumanizedType = (minutes: number) => string;
export const durationHumanizedKey = Symbol('durationHumanizedKey') as InjectionKey<DurationHumanizedType>;
