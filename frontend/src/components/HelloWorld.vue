<template>
  <div>
    <p v-if="userid > 0">You're logged in with ID {{ userid }}, have fun</p>
    <p v-else>Pleasy sign in first</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const userid = ref('');

async function getUserId() {
  const res = await fetch('http://localhost:5000/');
  userid.value = await res.json();
}

getUserId();
</script>
