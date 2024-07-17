// get the first key of given object that points to given value
import { ColorSchemes } from '@/definitions';
import { CustomEventData, Coloring, EventPopup, HTMLElementEvent, CalendarEvent } from './models';

// find a key by a given value and return it
export const keyByValue = (o: Object, v: number|string): number|string => Object.keys(o).find((k) => o[k] === v);

// create event color for border and background, inherited from calendar color attribute
export const eventColor = (event: CustomEventData, placeholder: Boolean): Coloring => {
  const color = {
    border: null,
    background: null,
  };
  // color appointment slots
  if (!placeholder) {
    color.border = event.calendar_color;
    color.background = event.calendar_color;
    // keep solid background only for slots with attendee
    if (!event.attendee && !event.remote) {
      color.background += '22';
    }
  }

  return color;
};

// create initials from given name
export const initials = (name: string): string => {
  if (name) {
    const parts = name.toUpperCase().split(' ');
    return parts.length > 1
      ? parts[0][0] + parts.at(-1)[0]
      : name[0];
  }
  return '';
};

// file download
export const download = (data: BlobPart, filename: string, contenttype: string = 'text/plain'): void => {
  const a = document.createElement('a');
  const file = new Blob([data], { type: `${contenttype};charset=UTF-8`, endings: 'native' });
  // TODO: use fetch or similar to programmatically trigger a download
  const url = URL.createObjectURL(file);
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }, 0);
};

// handle time format, return dayjs format string
// can be either set by the user (local storage) or detected from system
export const timeFormat = (): string => {
  const is12HourTime = Intl.DateTimeFormat().resolvedOptions().hour12 ? 12 : 24;
  const format = Number(localStorage?.getItem('timeFormat')) ?? is12HourTime;
  return format === 24 ? 'HH:mm' : 'hh:mm A';
};

// event popup handling
export const initialEventPopupData: EventPopup = {
  event: null,
  display: 'none',
  top: 0,
  left: 'initial',
};

// calculate properties of event popup for given element and show popup
export const showEventPopup = (el: HTMLElementEvent, event: CalendarEvent, position: string = 'right') => {
  const obj = { ...initialEventPopupData };
  obj.event = event.customData;
  obj.display = 'block';
  obj.top = `${el.target.offsetTop + el.target.clientHeight / 2 - el.target.parentElement.scrollTop}px`;
  if (!position || position === 'right') {
    obj.left = `${el.target.offsetLeft + el.target.clientWidth + 4}px`;
  }
  if (position === 'left') {
    obj.left = `${el.target.offsetLeft - 4}px`;
  }
  if (position === 'top') {
    obj.left = `${el.target.offsetLeft + el.target.clientWidth / 2}px`;
    obj.top = `${el.target.offsetTop - 50}px`;
  }
  return obj;
};

/**
 * Returns the stored locale setting or null if none is set.
 * TODO: This should be moved to a settings store
 */
export const getLocale = (): string|null => {
  const locale = localStorage?.getItem('locale');
  if (!locale) {
    return null;
  }
  return locale;
};

/**
 * Returns the stored theme value. If the stored value does not exist, it will guess based on prefers-color-scheme.
 * TODO: This should be moved to a settings store
 * @returns {ColorSchemes} - Colour theme value
 */
export const getPreferredTheme = (): string => {
  const theme = localStorage?.getItem('theme');
  if (!theme) {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? ColorSchemes.Dark : ColorSchemes.Light;
  }

  switch (theme) {
    case 'dark':
      return ColorSchemes.Dark;
    case 'light':
      return ColorSchemes.Light;
    default:
      // This would be ColorSchemes.System, but I feel like we need a definitive answer here.
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? ColorSchemes.Dark : ColorSchemes.Light;
  }
};

/**
 * via: https://stackoverflow.com/a/11868398
 */
export const getAccessibleColor = (hexcolor: string): string => {
  const defaultColor = getPreferredTheme() === ColorSchemes.Dark ? 'white' : 'black';
  if (!hexcolor) {
    return defaultColor;
  }
  const r = parseInt(hexcolor.substring(1, 3), 16);
  const g = parseInt(hexcolor.substring(3, 5), 16);
  const b = parseInt(hexcolor.substring(5, 7), 16);
  const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000;
  return (yiq >= 160) ? 'black' : 'white';
};

export default {
  keyByValue,
  eventColor,
  initials,
  download,
  timeFormat,
  initialEventPopupData,
  showEventPopup,
  getAccessibleColor,
  getLocale,
};
