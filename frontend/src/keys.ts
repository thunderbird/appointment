import { ConfigType, Dayjs, DayjsTimezone } from 'dayjs';
import { CreateDurationType } from 'dayjs/plugin/duration';
import { InjectionKey } from 'vue';
import { Fetch, Refresh } from '@/models';
import { IsoWeekday } from '@/composables/dayjs';

/**
 * These are typed Symbols for use with inject/provide in VueJS
 */

// Provides Dayjs class functionality as well as the timezone plugin, customParseFormat and related keys
type DayjsType = ((_?:ConfigType) => Dayjs) & {
  tz: DayjsTimezone,
  max: (...dayjs: Dayjs[]) => Dayjs | null,
  min: (...dayjs: Dayjs[]) => Dayjs | null,
  duration: CreateDurationType,
} & ((objToParse: any, format: string) => Dayjs);
export const dayjsKey = Symbol('dayjs') as InjectionKey<DayjsType>;
export const isoWeekdaysKey = Symbol('isoWeekdays') as InjectionKey<IsoWeekday[]>;
export const tzGuessKey = Symbol('tzGuess') as InjectionKey<string>;
export const isoFirstDayOfWeekKey = Symbol('isoFirstDayOfWeek') as InjectionKey<number>;

// Provide urls for API and booking
export const apiUrlKey = Symbol('apiUrl') as InjectionKey<string>;
export const bookingUrlKey = Symbol('bookingUrl') as InjectionKey<string>;

// Provide environment and authentication keys
export const isPasswordAuthKey = Symbol('isPasswordAuth') as InjectionKey<boolean>;
export const isFxaAuthKey = Symbol('isFxaAuth') as InjectionKey<boolean>;
export const fxaEditProfileUrlKey = Symbol('fxaEditProfileUrl') as InjectionKey<string>;
export const isAccountsAuthKey = Symbol('isAccountsAuth') as InjectionKey<boolean>;

// Provide configured fetch call to our backend API
export const callKey = Symbol('call') as InjectionKey<Fetch>;

// Provide a refresh data function
export const refreshKey = Symbol('refresh') as InjectionKey<Refresh>;

// Provide functionality to paint background of event objects
type PaintBackgroundType = (element: Event, hexColor: string, hexTransparency?: string, reset?: boolean) => void;
export const paintBackgroundKey = Symbol('paintBackground') as InjectionKey<PaintBackgroundType>;

// Provide duration data in human friendly form
type DurationHumanizedType = (minutes: number) => string;
export const durationHumanizedKey = Symbol('durationHumanized') as InjectionKey<DurationHumanizedType>;
