// get the first key of given object that points to given value
export const keyByValue = (o, v) => Object.keys(o).find((k) => o[k] === v);

// create event color for border and background, inherited from calendar color attribute
export const eventColor = (event, placeholder) => {
  const color = {
    border: null,
    background: null,
  };
  // color appointment slots
  if (!placeholder && !event.remote) {
    color.border = event.calendar_color;
    color.background = event.calendar_color;
    // keep solid background only for slots with attendee
    if (!event.attendee) {
      color.background += '22';
    }
  }
  // color remote tentative events
  if (event.remote && event.tentative) {
    color.border = `${event.calendar_color}bb`;
    color.background = 'transparent';
  }
  return color;
};

// create initials from given name
export const initials = (name) => {
  if (name) {
    const parts = name.toUpperCase().split(' ');
    return parts.length > 1
      ? parts[0][0] + parts.at(-1)[0]
      : name[0];
  }
  return '';
};

// file download
export const download = (data, filename, contenttype = 'text/plain') => {
  const a = document.createElement('a');
  const file = new Blob([data], { type: `${contenttype};charset=UTF-8`, endings: 'native' });
  // IE10+
  if (window.navigator.msSaveOrOpenBlob) {
    window.navigator.msSaveOrOpenBlob(file, filename);
  } else {
    // other browsers
    const url = URL.createObjectURL(file);
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    }, 0);
  }
};

// handle time format, return dayjs format string
// can be either set by the user (local storage) or detected from system
export const timeFormat = () => {
  const is12HourTime = Intl.DateTimeFormat().resolvedOptions().hour12 ? 12 : 24;
  const format = Number(localStorage?.getItem('timeFormat')) ?? is12HourTime;
  return format === 24 ? 'HH:mm' : 'hh:mm A';
};

// event popup handling
export const initialEventPopupData = {
  event: null,
  display: 'none',
  top: 0,
  left: 'initial',
};
// calculate properties of event popup for given element and show popup
export const showEventPopup = (el, event, position = 'right') => {
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
export const getAccessibleColor = (hexcolor) => {
  if (!hexcolor) {
    return 'white';
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
};
