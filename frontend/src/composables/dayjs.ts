import { App } from 'vue';
import dayjs from 'dayjs';
import advancedFormat from 'dayjs/plugin/advancedFormat';
import duration from 'dayjs/plugin/duration';
import isBetween from 'dayjs/plugin/isBetween';
import isoWeek from 'dayjs/plugin/isoWeek';
import isToday from 'dayjs/plugin/isToday';
import localeData from 'dayjs/plugin/localeData';
import localizedFormat from 'dayjs/plugin/localizedFormat';
import minMax from 'dayjs/plugin/minMax';
import relativeTime from 'dayjs/plugin/relativeTime';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import weekday from 'dayjs/plugin/weekday';
import customParseFormat from 'dayjs/plugin/customParseFormat';
import 'dayjs/locale/de';
import {
  dayjsKey, durationHumanizedKey, isoWeekdaysKey, tzGuessKey, isoFirstDayOfWeekKey,
} from '@/keys';

export type IsoWeekday = {
  iso: number,
  long: string,
  short: string,
  min: string,
};

export default function useDayJS(app: App<Element>, locale: string) {
  dayjs.locale(locale);
  dayjs.extend(advancedFormat);
  dayjs.extend(duration);
  dayjs.extend(isBetween);
  dayjs.extend(isoWeek);
  dayjs.extend(isToday);
  dayjs.extend(localeData);
  dayjs.extend(localizedFormat);
  dayjs.extend(minMax);
  dayjs.extend(relativeTime);
  dayjs.extend(utc);
  dayjs.extend(timezone);
  dayjs.extend(weekday);
  dayjs.extend(customParseFormat);

  // provide the configured dayjs instance as well es some helper functions
  // TODO: provide method to live update the dayjs locale
  app.provide(dayjsKey, dayjs);
  app.provide(tzGuessKey, dayjs.tz.guess());

  const durationHumanized = (minutes: number): string => ((minutes < 60)
    ? dayjs.duration(minutes, 'minutes').humanize()
    : dayjs.duration(minutes / 60, 'hours').humanize());
  app.provide(durationHumanizedKey, durationHumanized);

  // locale aware first day of week
  const firstDayOfWeek = dayjs.localeData().firstDayOfWeek();
  const isoFirstDayOfWeek = firstDayOfWeek === 0 ? 7 : firstDayOfWeek;
  app.provide(isoFirstDayOfWeekKey, isoFirstDayOfWeek);

  // provide unified list of locale weekdays with Monday=1 to Sunday=7 (isoweekdays)
  // taking locale first day of week into account
  const isoWeekdays = [] as IsoWeekday[];
  // TODO: generate order list for all starting days
  const order = isoFirstDayOfWeek === 7 ? [7, 1, 2, 3, 4, 5, 6] : [1, 2, 3, 4, 5, 6, 7];
  order.forEach((i) => {
    const n = i === 7 ? 0 : i;
    isoWeekdays.push({
      iso: i,
      long: dayjs.weekdays()[n],
      short: dayjs.weekdaysShort()[n],
      min: dayjs.weekdaysMin()[n],
    });
  });

  app.provide(isoWeekdaysKey, isoWeekdays);
}
