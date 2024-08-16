<script setup lang="ts">
import {
  computed, inject, onMounted, Ref, ref,
} from 'vue';
import { useI18n } from 'vue-i18n';
import { AlertSchemes, TableDataType } from '@/definitions';
import { useRouter } from 'vue-router';
import {
  WaitingListEntry,
  WaitingListResponse,
  BooleanResponse,
  TableDataRow,
  TableDataColumn,
  TableFilter,
  WaitingListInviteResponse
} from "@/models";
import { dayjsKey, callKey } from "@/keys";
import DataTable from '@/components/DataTable.vue';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';
import AlertBox from '@/elements/AlertBox.vue';
import AdminNav from '@/elements/admin/AdminNav.vue';
import PrimaryButton from "@/elements/PrimaryButton.vue";
import {IconSend} from "@tabler/icons-vue";

const router = useRouter();
const { t } = useI18n();

const call = inject(callKey);
const dj = inject(dayjsKey);

const waitingListUsers = ref<WaitingListEntry[]>([]);
const displayPage = ref(false);
const loading = ref(true);
const pageError = ref('');
const pageNotification = ref('');
const selectedFields = ref([]);
const dataTableRef = ref(null);

const filteredUsers = computed(() => waitingListUsers.value.map((user) => ({
  id: {
    type: TableDataType.Text,
    value: user.id,
  },
  email: {
    type: TableDataType.Text,
    value: user.email,
  },
  email_verified: {
    type: TableDataType.Text,
    value: user.email_verified ? 'Verified' : 'Not Verified',
  },
  invite_id: {
    type: TableDataType.Text,
    value: user.invite_id ?? 'Awaiting Access',
  },
  timeCreated: {
    type: TableDataType.Text,
    value: dj(user.time_created).format('ll LTS'),
  },
  timeUpdated: {
    type: TableDataType.Text,
    value: dj(user.time_updated).format('ll LTS'),
  },
} as TableDataRow)));
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
] as TableDataColumn[];
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
     */
    fn: (selectedKey: string, mutableDataList: TableDataRow[]) => {
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
     */
    fn: (selectedKey: string, mutableDataList: TableDataRow[]) => {
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
] as TableFilter[];

/**
 * Keep track of how many folks are selected
 * The data table just sends us a full list each time!
 * @param rows
 */
const onFieldSelect = async (rows: TableDataRow[]) => {
  selectedFields.value = [...rows];
};

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

const sendInvites = async () => {
  console.log("Send!");
  loading.value = true;

  const idList = selectedFields.value.map((row) => row.id.value);

  const response: WaitingListInviteResponse = await call('waiting-list/invite').post({id_list: idList}).json();
  const { data, error } = response;

  if (error.value) {

  }

  const { accepted, errors } = data.value;

  console.log(data.value);

  pageNotification.value = t('label.sentCountInvitesSuccessfully', {count: accepted.length})

  if (errors.length) {
    pageError.value = errors.join('\n');
  }

  // Unselect everything!
  selectedFields.value = [];
  dataTableRef.value.clearSelectedRows();

  await refresh();
  loading.value = false;
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
      style="white-space: break-spaces;
        line-height: 2;"
      @close="pageError = ''"
      v-if="pageError"
    >
      {{ pageError }}
    </alert-box>
  </div>
  <admin-nav/>
  <div v-if="displayPage">
    <data-table
      ref="dataTableRef"
      data-name="Waiting List Users"
      data-key="id"
      :allow-multi-select="true"
      :data-list="filteredUsers"
      :columns="columns"
      :filters="filters"
      :loading="loading"
      @fieldSelect="onFieldSelect"
    >
      <template v-slot:footer>
        <div class="flex w-1/3 flex-col gap-4 text-center md:w-full md:flex-row md:text-left">
          <label class="flex flex-col gap-4 md:flex-row md:items-center md:gap-0">
            <span>{{ t('label.sendInviteToWaitingList', {count: selectedFields.length}) }}</span>
          </label>
          <primary-button class="btn-send" :disabled="loading || selectedFields.length === 0" @click="sendInvites" :title="t('label.send')">
            <icon-send />
            {{ t('label.send') }}
          </primary-button>
        </div>
        <div>
          {{ t('waitingList.adminInviteNotice')}}
        </div>
      </template>
    </data-table>
  </div>
  <div v-else class="flex size-full min-h-[75vh] items-center justify-center">
    <loading-spinner/>
  </div>
</template>
