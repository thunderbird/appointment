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
import 'dayjs/locale/de';

export function useDayJS(app, locale) {
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

  // provide the configured dayjs instance as well es some helper functions
  // TODO: provide method to live update the dayjs locale
  app.provide('dayjs', dayjs);

  const hDuration = (m) => ((m < 60)
    ? dayjs.duration(m, 'minutes').humanize()
    : dayjs.duration(m / 60, 'hours').humanize());
  app.provide('hDuration', hDuration);

  // locale aware first day of week
  const firstDayOfWeek = dayjs.localeData().firstDayOfWeek();
  const isoFirstDayOfWeek = firstDayOfWeek === 0 ? 7 : firstDayOfWeek;
  app.provide('isoFirstDayOfWeek', isoFirstDayOfWeek);

  // provide unified list of locale weekdays with Monday=1 to Sunday=7 (isoweekdays)
  // taking locale first day of week into account
  const isoWeekdays = [];
  const order = isoFirstDayOfWeek === 7 ? [7, 1, 2, 3, 4, 5, 6] : [1, 2, 3, 4, 5, 6, 7]; // TODO: generate for all starts
  order.forEach((i) => {
    const n = i === 7 ? 0 : i;
    isoWeekdays.push({
      iso: i,
      long: dayjs.weekdays()[n],
      short: dayjs.weekdaysShort()[n],
      min: dayjs.weekdaysMin()[n],
    });
  });

  app.provide('isoWeekdays', isoWeekdays);
}
