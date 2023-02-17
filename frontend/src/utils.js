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
    const parts = name.split(' ');
    return parts.length > 1
      ? parts[0][0] + parts.at(-1)[0]
      : name[0];
  } else {
    return '';
  }
};

export default {
	keyByValue,
	eventColor,
  initials,
};
