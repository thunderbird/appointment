import { ConfigType, Dayjs, DayjsTimezone } from 'dayjs';
import { CreateDurationType } from 'dayjs/plugin/duration';
import { InjectionKey } from 'vue';
import { Fetch, Refresh } from '@/models';
import { IsoWeekday } from '@/composables/dayjs';

/**
 * These are typed Symbols for use with inject/provide in VueJS
 */

// Provides Dayjs class functionality as well as the timezone plugin, customParseFormat and related keys
type DayjsType = ((_?: ConfigType) => Dayjs) & {
  tz: DayjsTimezone,
  max: (...dayjs: Dayjs[]) => Dayjs | null,
  min: (...dayjs: Dayjs[]) => Dayjs | null,
  duration: CreateDurationType,
  locale: (preset?: string) => string,
} & ((objToParse: any, format: string) => Dayjs);
export const dayjsKey = Symbol('dayjs') as InjectionKey<DayjsType>;
export const isoWeekdaysKey = Symbol('isoWeekdays') as InjectionKey<IsoWeekday[]>;
export const tzGuessKey = Symbol('tzGuess') as InjectionKey<string>;

// Provide urls for API and booking
export const apiUrlKey = Symbol('apiUrl') as InjectionKey<string>;
export const shortUrlKey = Symbol('shortUrl') as InjectionKey<string>;

// Provide configured fetch call to our backend API
export const callKey = Symbol('call') as InjectionKey<Fetch>;

// Provide a refresh data function
export const refreshKey = Symbol('refresh') as InjectionKey<Refresh>;
