<script setup lang="ts">
import {
  computed, inject, onMounted, ref,
} from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { IconSend } from '@tabler/icons-vue';
import DataTable from '@/components/DataTable.vue';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';
import AlertBox from '@/elements/AlertBox.vue';
import AdminNav from '@/elements/admin/AdminNav.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import { dayjsKey, callKey } from '@/keys';
import {
  WaitingListEntry,
  WaitingListInvite,
  BooleanResponse,
  TableDataRow,
  TableDataColumn,
  TableFilter,
  WaitingListInviteResponse,
  Exception,
  ExceptionDetail,
  Alert,
} from '@/models';
import { AlertSchemes, TableDataType } from '@/definitions';
import { staggerRetrieve } from '@/utils';

const router = useRouter();
const { t } = useI18n();

const call = inject(callKey);
const dj = inject(dayjsKey);

const waitingListUsers = ref<WaitingListEntry[]>([]);
const displayPage = ref(false);
const loading = ref(true);
const pageError = ref<Alert>(null);
const pageNotification = ref<Alert>(null);
const selectedFields = ref([]);
const dataTableRef = ref(null);
const emailFilter = ref<string>(null);
const waitingListUsersList = computed(() => {
  if (emailFilter.value) {
    return waitingListUsers.value.filter((wl) => wl.email.match(new RegExp(RegExp.escape(emailFilter.value), 'gi')));
  }
  return waitingListUsers.value;
});

const filteredUsers = computed(() => waitingListUsersList.value.map((user) => ({
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
    value: user.email_verified ? t('label.verified') : t('label.notVerified'),
  },
  invite_id: {
    type: TableDataType.Text,
    value: user.invite_id ?? t('label.awaitingAccess'),
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
    name: t('label.id'),
  },
  {
    key: 'email',
    name: t('label.email'),
  },
  {
    key: 'email_verified',
    name: t('label.verifiedEmail'),
  },
  {
    key: 'invite_id',
    name: t('label.inviteId'),
  },
  {
    key: 'createdAt',
    name: t('label.timeCreated'),
  },
  {
    key: 'updatedAt',
    name: t('label.timeUpdated'),
  },
] as TableDataColumn[];
const filters = [
  {
    name: t('label.inviteStatus'),
    options: [
      {
        name: t('label.all'),
        key: 'all',
      },
      {
        name: t('label.accepted'),
        key: 'accepted',
      },
      {
        name: t('label.awaitingAccess'),
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
          return mutableDataList.filter((data) => (data.invite_id.value !== t('label.awaitingAccess')));
        case 'awaiting_access':
          return mutableDataList.filter((data) => (data.invite_id.value === t('label.awaitingAccess')));
        default:
          break;
      }
      return null;
    },
  },
  {
    name: t('label.emailVerifiedStatus'),
    options: [
      {
        name: t('label.all'),
        key: 'all',
      },
      {
        name: t('label.verified'),
        key: 'verified',
      },
      {
        name: t('label.notVerified'),
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
          return mutableDataList.filter((data) => (data.email_verified.value === t('label.verified')));
        case 'not_verified':
          return mutableDataList.filter((data) => (data.email_verified.value === t('label.notVerified')));
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
  pageError.value = null;

  waitingListUsers.value = await staggerRetrieve(
    (payload: object) => call('waiting-list/').post(payload).json(),
    250,
    pageError,
  );
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
  loading.value = true;

  const idList = selectedFields.value.map((row) => row.id.value);

  const response: WaitingListInviteResponse = await call('waiting-list/invite').post({ id_list: idList }).json();
  const { data, error } = response;

  if (error.value) {
    pageError.value = {
      title: ((data?.value as Exception)?.detail as ExceptionDetail)?.message ?? t('error.somethingWentWrong'),
    };
    loading.value = false;
    return;
  }

  const { accepted, errors } = data.value as WaitingListInvite;

  pageNotification.value = { title: t('label.sentCountInvitesSuccessfully', { count: accepted.length }) };

  if (errors.length) {
    pageError.value = { title: errors.join('\n') };
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
      v-if="pageNotification"
      :alert="pageNotification"
      :scheme="AlertSchemes.Success"
      @close="pageNotification = null"
    />
    <alert-box
      v-if="pageError"
      :alert="pageError"
      @close="pageError = null"
    />
  </div>
  <admin-nav/>
  <div v-if="displayPage">
    <data-table
      ref="dataTableRef"
      :data-name="t('label.waitingListUser', filteredUsers?.length)"
      data-key="id"
      :allow-multi-select="true"
      :data-list="filteredUsers"
      :columns="columns"
      :filters="filters"
      :loading="loading"
      @fieldSelect="onFieldSelect"
    >
      <template v-slot:footer>
        <div class="flex w-full">
        <div class="flex w-1/3 flex-col gap-4 text-center md:w-full md:flex-row md:text-left">
          <label class="flex flex-col gap-4 md:flex-row md:items-center md:gap-0">
            <span>{{ t('label.sendInviteToWaitingList', {count: selectedFields.length}) }}</span>
          </label>
          <primary-button
            class="btn-send"
            :disabled="loading || selectedFields.length === 0"
            @click="sendInvites"
            :title="t('label.send')"
          >
            <icon-send />
            {{ t('label.send') }}
          </primary-button>
        </div>
          <div class="flex flex-col items-end gap-4">
            <label class="flex flex-col gap-4 md:flex-row md:items-center md:gap-0">
              <span>{{ t('label.search') }}</span>
              <input
                class="mx-4 w-60 rounded-md text-sm"
                type="text"
                v-model="emailFilter"
                :disabled="loading"
                enterkeyhint="search"
              />
            </label>
          </div>
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
