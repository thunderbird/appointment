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
    color.border = event.calendar_color + 'bb';
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
  if (localStorage.getItem('timeFormat')) {
    return Number(localStorage.getItem('timeFormat')) === 24 ? 'H:mm' : 'h:mm A';
  }
  return 'LT';
};

export default {
  keyByValue,
  eventColor,
  initials,
  download,
  timeFormat,
};
