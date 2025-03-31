// get the first key of given object that points to given value
import { Ref } from 'vue';
import { i18nType } from '@/composables/i18n';
import {
  CustomEventData,
  Coloring,
  EventPopup,
  HTMLElementEvent,
  CalendarEvent,
  PydanticException,
  User,
  Alert,
  ListResponse,
} from '@/models';

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
export const enumToObject = (e: object): { [key in string]: number } => {
  const o = {};
  Object.keys(e).filter((v) => isNaN(Number(v))).forEach((k) => o[lcFirst(k)] = e[k]);
  return o;
};

// find a key by a given value and return it
export const keyByValue = (o: object, v: number|string, isEnum = false): number|string => {
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
// can be either set by the user (local storage) or detected from system.
// This functions works independent from Pinia stores so that
// it can be called even if stores are not initialized yet.
export const timeFormat = (): string => {
  const fallbackFormat = import.meta.env?.VITE_DEFAULT_HOUR_FORMAT ?? 12;
  const user = JSON.parse(localStorage?.getItem('tba/user') ?? '{}') as User;

  let use12HourTime = null;
  try {
    use12HourTime = Intl.DateTimeFormat(window.navigator.language, { hour: 'numeric' }).resolvedOptions()?.hour12 ?? null;
  } catch (_e: RangeError|any) {
    // Catch any range error raised by invalid language/locale codes and pass
  }

  // `.hour12` is an optional value and can be undefined (we cast it as null.) So default to our env value, and if not null use it.
  let detected = fallbackFormat;
  if (use12HourTime !== null) {
    detected = use12HourTime ? 12 : 24;
  }

  const format = Number(user.settings?.timeFormat ?? detected);
  return format === 24 ? 'HH:mm' : 'hh:mm A';
};

// Check if we already have a local user preferred language
// Otherwise just use the navigators language.
// This functions works independent from Pinia stores so that
// it can be called even if stores are not initialized yet.
export const defaultLocale = () => {
  const user = JSON.parse(localStorage?.getItem('tba/user') ?? '{}') as User;
  return user?.settings?.language ?? navigator.language.split('-')[0];
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
 * via: https://stackoverflow.com/a/11868398
 */
export const getAccessibleColor = (hexcolor: string): string => {
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
export const handleFormError = (i18n: i18nType, formRef: Ref, errObj: PydanticException): Alert => {
  const unknownError = i18n('error.somethingWentWrong');
  if (!errObj) {
    return { title: unknownError };
  }

  const fields = formRef.value.elements as HTMLFormControlsCollection;

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
    return { title: detail };
  } else {
    return {
      title: detail?.message ?? unknownError,
      details: detail?.reason,
    };
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

export const sleep = async (timeMs: number) => new Promise((resolve) => { window.setTimeout(resolve, timeMs); });

/**
 * Retrieve all the items from a ListResponse route staggered by 250ms per page.
 * @param requestFn
 * @param perPage
 * @param pageError
 */
export const staggerRetrieve = async (requestFn: any, perPage: number, pageError?: Ref<Alert>) => {
  // Load the first page to get the total amount of pages
  const response: ListResponse = await requestFn({
    page: 1,
    per_page: perPage,
  });
  const { data } = response;

  if (!data.value?.page_meta) {
    pageError.value = {
      title: 'Remote request error',
      details: 'There was a problem loading the list. Please try again.',
    };
    return null;
  }

  const { page, total_pages: totalPages } = data.value.page_meta;
  const { items } = data.value;
  let itemList = [...items];

  const promises = [];
  // Queue up the remainder of the pages as promises
  for (let i = page + 1; i < totalPages + 1; i += 1) {
    promises.push((async () => {
      // Stagger calls to avoid overloading the db
      await sleep(250 * i);
      return requestFn({
        page: i,
        per_page: perPage,
      });
    })());
  }

  // Execute them all at once
  const promiseResponses = await Promise.all(promises);
  promiseResponses.forEach((_response) => {
    const { data: _data } = _response;
    // We don't have page info in this context, so just display a generic error...
    if (!_data.value?.items) {
      pageError.value = {
        title: 'Remote request error',
        details: 'There was a problem loading some items. Please refresh and try again.',
      };
      return;
    }
    itemList = itemList.concat(_data.value?.items ?? []);
  });

  return itemList;
};

export default {
  keyByValue,
  eventColor,
  initials,
  download,
  timeFormat,
  defaultLocale,
  initialEventPopupData,
  showEventPopup,
  getAccessibleColor,
  handleFormError,
  sleep,
};
