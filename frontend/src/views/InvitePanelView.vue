<template>
  <!-- page title area -->
  <div v-if="user.exists()" class="flex flex-col items-center justify-center gap-4">
    <div class="flex flex-row justify-between items-center w-full">
      <div>
        <span class="font-bold">{{ filteredInvites.length }}</span> invite codes
      </div>
      <list-pagination
        :list-length="filteredInvites.length"
        :page-size="pageSize"
        @update="updatePage"
      />
      <div class="flex items-center justify-end gap-2 text-right">
        <label for="used-filter" class="whitespace-nowrap">Used Filter</label>
        <select id="used-filter" class="rounded-md" v-model="usedFilter">
          <option value="all">Show All</option>
          <option value="unused">Show Unused</option>
          <option value="used">Show Used</option>
        </select>

        <label for="status-filter" class="whitespace-nowrap">Status Filter</label>
        <select id="status-filter" class="rounded-md" v-model="inviteFilter">
          <option value="all">Show All</option>
          <option value="available">Show Available</option>
          <option value="revoked">Show Revoked</option>
        </select>
      </div>
    </div>
    <div class="
      rounded-xl w-full border py-2 border-gray-100 bg-white text-sm shadow-sm
      dark:border-gray-500 dark:bg-gray-700 mb-4 ml-auto mr-0
    ">
      <table>
        <thead>
          <tr>
            <th>Code</th>
            <th>Used</th>
            <th>Status</th>
            <th>Time Created</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="invite in paginatedInvites" :key="invite.code">
            <td><code>{{ invite.code }}</code></td>
            <td>{{ invite.subscriber_id !== null ? 'Yes' : 'No' }}</td>
            <td>{{ invite.status === 1 ? 'Available' : 'Revoked' }}</td>
            <td class="whitespace-nowrap">{{ dj(invite.time_created).format('ll LTS') }}</td>
            <td class="w-28 py-2">
              <caution-button
                v-if="invite.status !== 2"
                :label="'Revoke'"
                class="text-sm px-4 h-8"
                @click="revokeInvite(invite.code)"
              />
            </td>
          </tr>
          <tr v-if="filteredInvites.length === 0">
            <td colspan="5">No invites of this type could be found.</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <th colspan="5">
              <div class="flex w-full gap-4">
                <label>
                  Generate
                  <input
                    class="w-20 rounded-md text-sm"
                    type="number"
                    placeholder="Amount"
                    v-model="amountOfInvitesToGenerate"
                  />
                  invite codes. They will be added to this list.
                </label>
                <primary-button :label="'Generate'" @click="generateInvites" />
              </div>
            </th>
          </tr>
        </tfoot>
      </table>
    </div>
  </div>
</template>

<style scoped>
/*
 * Not dealing with tailwinding every single td
 */
table {
  @apply w-full table-auto border-collapse bg-white text-sm shadow-sm dark:bg-gray-600;
}

thead, tfoot {
  @apply border-gray-200 bg-gray-100 dark:border-gray-500 dark:bg-gray-700 text-gray-600 dark:text-gray-300;
}

th {
  @apply px-4 text-left font-semibold border-gray-200 dark:border-gray-500;
}
thead th {
  @apply pb-4 pt-2;
}
tfoot th {
  @apply pb-2 pt-4;
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
import { computed, inject, onMounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { subscriberLevels } from '@/definitions';
import { useUserStore } from '@/stores/user-store';
import { storeToRefs } from 'pinia';
import PrimaryButton from '@/elements/PrimaryButton';
import CautionButton from '@/elements/CautionButton.vue';
import ListPagination from '@/elements/ListPagination.vue';

// icons
import { IconPencil } from '@tabler/icons-vue';
import { useRouter } from 'vue-router';

// component constants
const user = useUserStore();
const call = inject('call');
const dj = inject('dayjs');

// component constants
const { t } = useI18n();

// pagination
const pageSize = 10;
const currentPage = ref(0);
const updatePage = (index) => {
  currentPage.value = index;
}

// invite specific props
const usedFilter = ref('all');
const inviteFilter = ref('all');
const invites = ref([]);
const amountOfInvitesToGenerate = ref(0);

// reset page when filter changes
watch([usedFilter, inviteFilter], () => {
  currentPage.value = 0;
});

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

const paginatedInvites = computed(() => {
  return filteredInvites.value.length
    ? filteredInvites.value.slice(currentPage.value*pageSize, (currentPage.value+1)*pageSize)
    : [];
});

const getInvites = async () => {
  const response = await call('invite/').get().json();
  const { data } = response;

  invites.value = data.value;
};

const generateInvites = async () => {
  // Parse it as an integer to remove any bad bits
  const amount = parseInt(`${amountOfInvitesToGenerate.value}`, 10);
  if (!amount) {
    return;
  }

  amountOfInvitesToGenerate.value = 0;

  const response = await call(`invite/generate/${amount}`).post().json();
  const { data } = response;

  invites.value = [...invites.value, ...data.value];
};

const revokeInvite = async (code) => {
  // Parse it as a string to remove any bad bits..this probably works fine right?
  if (!code) {
    return;
  }

  const response = await call(`invite/revoke/${code}`).put().json();
  const { data } = response;

  if (data.value) {
    await getInvites();
  }
};

onMounted(async () => {
  await getInvites();
});

</script>
