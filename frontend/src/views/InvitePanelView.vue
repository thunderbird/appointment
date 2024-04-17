<template>
  <!-- page title area -->
  <div v-if="user.exists()" class="flex flex-col items-center justify-center gap-4">
    <div class="flex w-full flex-row justify-between">
      <div class="flex w-full items-center text-left">
        <a href="#generate">Go to Generate Invites</a>
      </div>
      <div class="flex w-full items-center justify-end gap-2 text-right">
        <label for="used-filter">Used Filter</label>
        <select id="used-filter" class="rounded-md" v-model="usedFilter">
          <option value="all">Show All</option>
          <option value="unused">Show Unused</option>
          <option value="used">Show Used</option>
        </select>

        <label for="status-filter">Status Filter</label>
        <select id="status-filter" class="rounded-md" v-model="inviteFilter">
          <option value="all">Show All</option>
          <option value="available">Show Available</option>
          <option value="revoked">Show Revoked</option>
        </select>
      </div>
    </div>
    <div class="round-support-div mb-4 ml-auto mr-0">
      <table>
        <thead>
        <tr>
          <th>Code</th>
          <th>Used</th>
          <th>Status</th>
          <th>Time Created</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="invite in filteredInvites" :key="invite.code">
          <td>{{ invite.code }}</td>
          <td>{{ invite.subscriber_id !== null ? 'Yes' : 'No' }}</td>
          <td>{{ invite.status === 1 ? 'Available' : 'Revoked' }}</td>
          <td>{{ invite.time_created }}</td>
        </tr>
        <tr v-if="filteredInvites.length === 0">
          <td colspan="4">No invites of this type could be found.</td>
        </tr>
        </tbody>
      </table>
    </div>
    <div id="generate" class="w-full">
      <div class="flex w-full max-w-xs flex-col gap-4">
        <label for="invite-amount">Generate Invites</label>
        <input id="invite-amount" class="w-full rounded-md text-sm" type="number" placeholder="Amount" v-model="amountOfInvitesToGenerate"/>
        <p>Generate {{ amountOfInvitesToGenerate }} invites. They will be added to the list below.</p>
        <div class="max-w-xs">
          <primary-button @click="generateInvites">Generate!</primary-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/*
 * Not dealing with tailwinding every single td
 */
.round-support-div {
  @apply rounded-t-xl w-full border pt-2 border-gray-100 bg-white text-sm shadow-sm dark:border-gray-500 dark:bg-gray-700;
}

table {
  @apply w-full table-auto border-collapse bg-white text-sm shadow-sm dark:bg-gray-600;
}

thead {
  @apply border-gray-200 bg-gray-100 dark:border-gray-500 dark:bg-gray-700 text-gray-600 dark:text-gray-300;
}

th {
  @apply w-1/2 p-4 text-left font-semibold border-gray-200 dark:border-gray-500;
}

td {
  @apply border border-gray-200 p-4 dark:border-gray-500;
}

td:first-child {
  @apply border-l-0;
}

td:last-child {
  @apply border-r-0;
}
</style>

<script setup>
import {
  computed, inject, onMounted, ref,
} from 'vue';
import { keyByValue } from '@/utils';
import { useI18n } from 'vue-i18n';
import { subscriberLevels } from '@/definitions';
import { useUserStore } from '@/stores/user-store';
import { storeToRefs } from 'pinia';
import PrimaryButton from '@/elements/PrimaryButton';
import SecondaryButton from '@/elements/SecondaryButton';

// icons
import { IconPencil } from '@tabler/icons-vue';
import { useRouter } from 'vue-router';

// component constants
const user = useUserStore();
const call = inject('call');

// component constants
const { t } = useI18n();

const usedFilter = ref('all');
const inviteFilter = ref('all');
const invites = ref([]);
const amountOfInvitesToGenerate = ref(0);

const filteredInvites = computed(() => {
  if (inviteFilter.value === 'all' && usedFilter.value === 'all') {
    return invites.value;
  }

  let filtered = invites.value;
  if (inviteFilter.value !== 'all') {
    filtered = filtered.filter((invite) => (invite.status === 1 ? inviteFilter.value === 'available' : inviteFilter.value !== 'available'));
  }

  if (usedFilter.value !== 'all') {
    filtered = filtered.filter((invite) => (invite.subscriber_id === null ? usedFilter.value === 'unused' : usedFilter.value !== 'unused'));
  }

  return filtered;
});

const getInvites = async () => {
  const response = await call('invite/').get().json();
  const { data } = response;

  invites.value = data.value;
};

const generateInvites = async () => {
  // Parse it as a string to remove any bad bits..this probably works fine right?
  const amount = parseInt(`${amountOfInvitesToGenerate.value}`, 10);
  if (!amount) {
    return;
  }

  amountOfInvitesToGenerate.value = 0;

  const response = await call(`invite/generate/${amount}`).post().json();
  const { data } = response;

  invites.value = [...invites.value, ...data.value];
};

onMounted(async () => {
  await getInvites();
  console.log(amountOfInvitesToGenerate.value);
});

</script>
