<template>
  <div>
    <h1>Thunderbird Appointment</h1>
    <div v-if="user && calendars">
      <h3>You're logged in as</h3>
      <pre>{{ user }}</pre>

      <h3>Your calendars</h3>
      <div v-for="cal in calendars" :key="cal.id">
        <code>[{{ cal.id }}] {{ cal.url }}</code> <i>{{ cal.title }}</i> (user: {{ cal.user }})
        <button @click="removeCalendar(cal.id)">Remove</button>
      </div><br>
      <input v-model="newCalendar.url" type="url" placeholder="url" />
      <input v-model="newCalendar.user" type="text" placeholder="user" />
      <input v-model="newCalendar.password" type="password" placeholder="password" />
      <button @click="addCalendar">Connect calendar</button>

      <h3>Your Appointments</h3>
      <div v-for="apmt in appointments" :key="apmt.id">
        <code>[{{ apmt.id }}]</code> <i>{{ apmt.title }}</i> ({{ apmt.duration }}min, <a :href="'http://localhost:8080/admin/' + apmt.slug">Public Link</a>)
        <ul>
          <li v-for="(s, i) in apmt.slots" :key="i">
            {{ s.start }} <button @click="saveEvent(user.username, apmt.slug, apmt.title, s.start, '2022-09-30T20:51:00')">Select</button>
          </li>
        </ul>
      </div><br>
      <select v-model="newAppointment.appointment.calendar_id">
        <option v-for="cal in calendars" :value="cal.id" :key="cal.id">{{ cal.title }}</option>
      </select>
      <input v-model="newAppointment.appointment.duration" type="number" placeholder="duration" />
      <input v-model="newAppointment.appointment.title" type="text" placeholder="title" />
      <input v-model="slot1" type="datetime-local" />
      <input v-model="slot2" type="datetime-local" />
      <button @click="addAppointment">Create Appointment</button>
    </div>
    <div v-else>Pleasy sign in first</div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';

const user = ref(null);
const calendars = ref(null);
const appointments = ref(null);
const slot1 = ref(null);
const slot2 = ref(null);
const newCalendar = reactive({
  url: '',
  user: '',
  password: ''
});
const newAppointment = reactive({
  appointment: {
    calendar_id: 0,
    duration: 0,
    title: '',
  },
  slots: []
});

const getUser = async () => {
  const res = await fetch('http://localhost:5000/login');
  user.value = await res.json();
};

const getCalendars = async () => {
  const res = await fetch('http://localhost:5000/me/calendars');
  calendars.value = await res.json();
};

const getAppointments = async () => {
  const res = await fetch('http://localhost:5000/me/appointments');
  appointments.value = await res.json();
};

const addCalendar = async () => {
  const res = await fetch(
    'http://localhost:5000/cal',
    {
      method: 'POST',
      body: JSON.stringify(newCalendar),
      headers: { 'Content-Type': 'application/json' }
    }
  );
  await res.json();
  getCalendars();
};

const addAppointment = async () => {
  newAppointment.slots.push({ start: slot1 }, { start: slot2 });
  const res = await fetch(
    'http://localhost:5000/apmt',
    {
      method: 'POST',
      body: JSON.stringify(newAppointment),
      headers: { 'Content-Type': 'application/json' }
    }
  );
  await res.json();
  getAppointments();
};

const saveEvent = async (username, slug, title, start, end) => {
  const res = await fetch(
    'http://localhost:5000/rmt/apmt/' + username + '/' + slug,
    {
      method: 'POST',
      body: JSON.stringify({
        title: title,
        start: start,
        end: end
      }),
      headers: { 'Content-Type': 'application/json' }
    }
  );
  await res.json();
};

const removeCalendar = async (id) => {
  const res = await fetch(
    'http://localhost:5000/cal/' + id,
    {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' }
    }
  );
  await res.json();
  getCalendars();
};

getUser();
getCalendars();
getAppointments();
</script>
