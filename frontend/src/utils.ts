// get the first key of given object that points to given value
import { ColorSchemes } from '@/definitions';
import { Ref } from 'vue';
import { i18nType } from '@/composables/i18n';
import {
  CustomEventData, Coloring, EventPopup, HTMLElementEvent, CalendarEvent, PydanticException,
} from './models';

/**
* Lowercases the first character of a string
*/
export const lcFirst = (s: string): string => {
  if (typeof s !== 'string' || !s) {
    return '';
  }

  return s[0].toLowerCase() + s.slice(1);
};

// Convert a numeric enum to an object for key-value iteration
export const enumToObject = (e: Object): { [key in string]: number } => {
  const o = {};
  Object.keys(e).filter((v) => isNaN(Number(v))).forEach((k) => o[lcFirst(k)] = e[k]);
  return o;
};

// find a key by a given value and return it
export const keyByValue = (o: Object, v: number|string, isEnum = false): number|string => {
  const e = isEnum ? enumToObject(o) : o;
  return Object.keys(e).find((k) => e[k] === v);
};

// create event color for border and background, inherited from calendar color attribute
export const eventColor = (event: CustomEventData, placeholder: boolean): Coloring => {
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
export const showEventPopup = (el: HTMLElementEvent, event: CalendarEvent, position: string = 'right'): EventPopup => {
  const obj = { ...initialEventPopupData };
  obj.event = event;
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

/**
 * Handles Pydantic errors, returns a form-level error message
 * or null if the error has to do with individual fields
 * @param i18n - i18n instance
 * @param formRef
 * @param errObj
 */
export const handleFormError = (i18n: i18nType, formRef: Ref, errObj: PydanticException) => {
  const unknownError = i18n('error.somethingWentWrong');
  if (!errObj) {
    return unknownError;
  }

  const fields = formRef.value.elements;
  const { detail } = errObj;

  if (Array.isArray(detail)) {
    detail.forEach((err) => {
      const name = err?.loc[1];
      if (name) {
        // Could either be in the context, or as a general message
        const msg = err?.ctx?.reason ?? err.msg;
        fields[name].setCustomValidity(msg);
      }
    });
  } else if (typeof detail === 'string') { // HttpException errors are just strings
    return detail;
  } else {
    return detail?.message ?? unknownError;
  }

  // Finally report it!
  formRef.value.reportValidity();
  return null;
};

/**
 * Clears any existing form errors
 * @param formRef
 */
export const clearFormErrors = (formRef: Ref) => {
  const { elements } = formRef.value;
  // HTMLCollection doesn't support .forEach lol
  for (const element of elements) {
    element.setCustomValidity('');
  }
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
  handleFormError,
};
