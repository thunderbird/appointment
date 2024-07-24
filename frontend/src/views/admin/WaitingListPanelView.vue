<script setup lang="ts">
import {
  computed, inject, onMounted, ref,
} from 'vue';
import { useI18n } from 'vue-i18n';
import { AlertSchemes, tableDataType } from '@/definitions';
import { useRouter } from 'vue-router';
import { WaitingListEntry, WaitingListResponse, BooleanResponse, Exception } from "@/models";
import { dayjsKey, callKey } from "@/keys";
import DataTable from '@/components/DataTable.vue';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';
import AlertBox from '@/elements/AlertBox.vue';
import AdminNav from '@/elements/admin/AdminNav.vue';

const router = useRouter();
const { t } = useI18n();

const call = inject(callKey);
const dj = inject(dayjsKey);

const waitingListUsers = ref<WaitingListEntry[]>([]);
const displayPage = ref(false);
const loading = ref(true);
const pageError = ref('');
const pageNotification = ref('');

const filteredUsers = computed(() => waitingListUsers.value.map((user) => ({
  id: {
    type: tableDataType.text,
    value: user.id,
  },
  email: {
    type: tableDataType.text,
    value: user.email,
  },
  email_verified: {
    type: tableDataType.text,
    value: user.email_verified ? 'Verified' : 'Not Verified',
  },
  invite_id: {
    type: tableDataType.text,
    value: user.invite_id ?? 'Awaiting Access',
  },
  timeCreated: {
    type: tableDataType.text,
    value: dj(user.time_created).format('ll LTS'),
  },
  timeUpdated: {
    type: tableDataType.text,
    value: dj(user.time_updated).format('ll LTS'),
  },
})));
const columns = [
  {
    key: 'id',
    name: 'Id',
  },
  {
    key: 'email',
    name: 'Email',
  },
  {
    key: 'email_verified',
    name: 'Verified Email',
  },
  {
    key: 'invite_id',
    name: 'Invite ID',
  },
  {
    key: 'createdAt',
    name: 'Time Created',
  },
  {
    key: 'updatedAt',
    name: 'Time Updated',
  },
];
const filters = [
  {
    name: 'Invite Status',
    options: [
      {
        name: 'All',
        key: 'all',
      },
      {
        name: 'Accepted',
        key: 'accepted',
      },
      {
        name: 'Awaiting Access',
        key: 'awaiting_access',
      },
    ],
    /**
     * Callback function, filter the list by selectedKey and return it back to the table
     * TODO: Add types when DataTable.vue is typed
     * @param selectedKey
     * @param mutableDataList
     * @returns {*}
     */
    fn: (selectedKey, mutableDataList) => {
      switch (selectedKey) {
        case 'all':
          return null;
        case 'accepted':
          return mutableDataList.filter((data) => (data.invite_id.value !== 'Awaiting Access'));
        case 'awaiting_access':
          return mutableDataList.filter((data) => (data.invite_id.value === 'Awaiting Access'));
        default:
          break;
      }
      return null;
    },
  },
  {
    name: 'Email Verified Status',
    options: [
      {
        name: 'All',
        key: 'all',
      },
      {
        name: 'Verified',
        key: 'verified',
      },
      {
        name: 'Not Verified',
        key: 'not_verified',
      },
    ],
    /**
     * Callback function, filter the list by selectedKey and return it back to the table
     * TODO: Add types when DataTable.vue is typed
     * @param selectedKey
     * @param mutableDataList
     * @returns {*}
     */
    fn: (selectedKey, mutableDataList) => {
      switch (selectedKey) {
        case 'all':
          return null;
        case 'verified':
          return mutableDataList.filter((data) => (data.email_verified.value === 'Verified'));
        case 'not_verified':
          return mutableDataList.filter((data) => (data.email_verified.value === 'Not Verified'));
        default:
          break;
      }
      return null;
    },
  },
];

/**
 * Retrieve waiting list entries
 */
const getInvites = async () => {
  const response: WaitingListResponse = await call('waiting-list/').get().json();
  const { data } = response;

  waitingListUsers.value = data.value as WaitingListEntry[];
};

/**
 * Update list of all existing waiting list entries
 */
const refresh = async () => {
  loading.value = true;
  await getInvites();
  loading.value = false;
};

const amIAdmin = async () => {
  const response: BooleanResponse = await call('permission-check').post().json();
  const { error } = response;

  return !error.value;
};

onMounted(async () => {
  const okToContinue = await amIAdmin();
  if (!okToContinue) {
    await router.replace('/');
    return;
  }
  displayPage.value = true;
  await refresh();
});

</script>

<template>
  <div class="flex w-full justify-center">
    <alert-box
      @close="pageNotification = ''"
      v-if="pageNotification"
      :scheme="AlertSchemes.Success"
    >
      {{ pageNotification }}
    </alert-box>
    <alert-box
      @close="pageError = ''"
      v-if="pageError"
    >
      {{ pageError }}
    </alert-box>
  </div>
  <admin-nav/>
  <div v-if="displayPage">
    <data-table
      data-name="Waiting List Users"
      :allow-multi-select="false"
      :data-list="filteredUsers"
      :columns="columns"
      :filters="filters"
      :loading="loading"
    >
    </data-table>
  </div>
  <div v-else class="flex size-full min-h-[75vh] items-center justify-center">
    <loading-spinner/>
  </div>
</template>
