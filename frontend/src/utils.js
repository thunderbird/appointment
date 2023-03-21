// get the first key of given object that points to given value
export const keyByValue = (o, v) => Object.keys(o).find(k => o[k]===v);

// create event color for border and background, inherited from calendar color attribute
export const eventColor = (event, placeholder) => {
  const color = {
    border:     null,
    background: null,
  };
  // only color appointment slots
  if (!placeholder && !event.remote) {
    color.border = event.calendar_color;
    color.background = event.calendar_color;
    // keep solid background only for slots with attendee
    if (!event.attendee) {
      color.background += '22';
    }
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
  } else {
    return '';
  }
};

// file download
export const download = (data, filename, contenttype='text/plain') => {
  let a = document.createElement('a');
  let file = new Blob([data], { type: contenttype + ';charset=UTF-8', endings: 'native' });
  // IE10+
  if (window.navigator.msSaveOrOpenBlob) {
    window.navigator.msSaveOrOpenBlob(file, filename);
  }
  // other browsers
  else {
    let url = URL.createObjectURL(file);
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

export default {
	keyByValue,
	eventColor,
  initials,
  download,
};
