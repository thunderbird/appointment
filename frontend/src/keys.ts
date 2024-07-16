import { ConfigType, Dayjs, DayjsTimezone } from 'dayjs';
import { InjectionKey } from 'vue';
import { Fetch } from '@/models';

/**
 * These are typed Symbols for use with inject/provide in VueJS
 */

// ...this works, don't touch.
/**
 * Provides Dayjs class functionality as well as the timezone plugin
 */
type DayjsType = ((_?:ConfigType) => Dayjs) & {
  tz: DayjsTimezone
};

export const dayjsKey = Symbol('dayjs') as InjectionKey<DayjsType>;
export const callKey = Symbol('call') as InjectionKey<Fetch>;
