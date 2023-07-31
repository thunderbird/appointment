import { ref, watch } from 'vue';

const STORAGE_KEY = 'tba/user';

const keys = [
  'email',
  'level',
  'name',
  'timezone',
  'username',
];

let userObj = null;

function load() {
  // Retrieve values from localStorage
  const jsonData = localStorage.getItem(STORAGE_KEY);
  if (jsonData) {
    try {
      const data = JSON.parse(jsonData);
      userObj = {
        ...data,
      };
    } catch (e) {
      // console.log('Could not parse user from localStorage');
    }
  }
}

function store(data) {
  try {
    const jsonData = JSON.stringify(data);
    localStorage.setItem(STORAGE_KEY, jsonData);
  } catch (e) {
    // console.log('Could not stringify and store to localStorage');
  }
}

function copyRefValuesToObj(aRef, obj) {
  keys.forEach((k) => {
    try {
      obj[k] = aRef[k] ?? aRef.value[k];
    } catch (e) {
      // console.log(e);
    }
  });
}

// Attempt initial load of data
load();
export const userStore = ref(userObj);

// Store in localStorage on update
watch(userStore, (newUser) => {
  const data = {};
  copyRefValuesToObj(newUser, data);
  store(data);
});

export function removeUserFromStorage() {
  localStorage.removeItem(STORAGE_KEY);
}

export function updateUserInStorage(obj) {
  // Provides a way to update the userStore
  // from a component that received it as a prop
  const data = {};
  copyRefValuesToObj(userStore, data);
  store({
    ...data,
    ...obj,
  });
}
