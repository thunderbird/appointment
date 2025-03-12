<script setup lang="ts">
import {
  computed, inject, onMounted, ref,
} from 'vue';
import { IconSend } from '@tabler/icons-vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import AdminNav from '@/elements/admin/AdminNav.vue';
import AlertBox from '@/elements/AlertBox.vue';
import DataTable from '@/components/DataTable.vue';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import ConfirmationModal from '@/components/ConfirmationModal.vue';
import { dayjsKey, callKey } from '@/keys';
import {
  Subscriber, SubscriberListResponse, BooleanResponse, Exception, TableDataRow, TableDataColumn, TableFilter, Alert,
} from '@/models';
import { useUserStore } from '@/stores/user-store';
import { AlertSchemes, TableDataButtonType, TableDataType } from '@/definitions';
import { sleep, staggerRetrieve } from '@/utils';

const user = useUserStore();

const router = useRouter();
const { t } = useI18n();

const call = inject(callKey);
const dj = inject(dayjsKey);

const subscribers = ref<Subscriber[]>([]);
const displayPage = ref(false);
const inviteEmail = ref('');
const loading = ref(true);
const pageError = ref<Alert>(null);
const pageNotification = ref<Alert>(null);
const hardDeleteModalOpen = ref<boolean>(false);
const hardDeleteModalContext = ref<Subscriber>(null);
const emailFilter = ref<string>(null);
const subscriberList = computed(() => {
  if (emailFilter.value) {
    return subscribers.value.filter((sub) => sub.email.match(emailFilter.value));
  }
  return subscribers.value;
});

const filteredSubscribers = computed(() => subscriberList.value.map((subscriber) => ({
  id: {
    type: TableDataType.Text,
    value: subscriber.id,
  },
  username: {
    type: TableDataType.Text,
    value: subscriber.username,
  },
  email: {
    type: TableDataType.Text,
    value: subscriber.email,
  },
  timeCreated: {
    type: TableDataType.Text,
    value: dj(subscriber.time_created).format('ll LTS'),
  },
  timeDeleted: {
    type: TableDataType.Text,
    value: subscriber.time_deleted ? dj(subscriber.time_deleted).format('ll LTS') : '',
  },
  timezone: {
    type: TableDataType.Text,
    value: subscriber.timezone ?? 'Unset',
  },
  wasInvited: {
    type: TableDataType.Bool,
    value: Boolean(subscriber.invite),
  },
  disable: {
    type: TableDataType.Button,
    buttonType: subscriber.time_deleted ? TableDataButtonType.Primary : TableDataButtonType.Caution,
    value: subscriber.time_deleted ? 'Enable' : 'Disable',
    disabled: !subscriber.time_deleted && subscriber.email === user.data.email,
  },
  hardDelete: {
    type: TableDataType.Button,
    buttonType: TableDataButtonType.Caution,
    value: 'Hard Delete',
    disabled: !subscriber.time_deleted || subscriber.email === user.data.email,
    tooltip: 'Completely remove the user from the database. This is the same as deleting someones account!! You must disable the account first.',
  },
} as TableDataRow)));
const columns = [
  {
    key: 'id',
    name: 'ID',
  },
  {
    key: 'username',
    name: 'Username',
  },
  {
    key: 'email',
    name: 'Email',
  },
  {
    key: 'createdAt',
    name: 'Time Created',
  },
  {
    key: 'deletedAt',
    name: 'Time Deleted',
  },
  {
    key: 'timezone',
    name: 'Timezone',
  },
  {
    key: 'wasInvited',
    name: 'Was Invited?',
  },
  {
    key: 'disable',
    name: '',
  },
  {
    key: 'hard delete',
    name: '',
  },
] as TableDataColumn[];
const filters = [
  {
    name: 'Was Invited',
    options: [
      {
        name: 'All',
        key: 'all',
      },
      {
        name: 'Yes',
        key: 'true',
      },
      {
        name: 'No',
        key: 'false',
      },
    ],
    /**
     * Callback function, filter the list by selectedKey and return it back to the table
     */
    fn: (selectedKey: string, mutableDataList: TableDataRow[]) => {
      if (selectedKey === 'all') {
        return mutableDataList;
      }
      return mutableDataList.filter((data) => data.wasInvited.value?.toString().toLowerCase() === selectedKey);
    },
  },
] as TableFilter[];

/**
 * Retrieve list of all existing subscribers
 */
const getSubscribers = async () => {
  pageError.value = null;

  subscribers.value = await staggerRetrieve(
    (payload: object) => call('subscriber/').post(payload).json(),
    250,
    pageError,
  );
};

/**
 * Update list of all existing subscribers
 */
const refresh = async () => {
  loading.value = true;
  await getSubscribers();
  loading.value = false;
};

/**
 * Disables a subscriber
 * @param email
 * @param currentState True if currently enabled (= not deleted)
 */
const toggleSubscriberState = async (email: string, currentState: boolean) => {
  if (!email) {
    return;
  }

  const action = currentState ? 'disable' : 'enable';
  const response: BooleanResponse = await call(`subscriber/${action}/${email}`).put().json();
  const { data } = response;

  if (data.value) {
    await refresh();
  }
};

/**
 * Update list of all existing subscribers
 */
const sendInvite = async () => {
  loading.value = true;
  pageError.value = null;
  pageNotification.value = null;

  const response = await call('invite/send').post({
    email: inviteEmail.value,
  }).json();

  const { data, error } = response;

  if (error.value) {
    const errorObj = (data.value as Exception)?.detail;

    if (!errorObj) {
      pageError.value = { title: t('error.somethingWentWrong') };
    } else if (errorObj instanceof Array) {
      pageError.value = { title: errorObj.map((err) => err.msg).join('\n') };
    } else {
      pageError.value = { title: data.value?.detail?.message };
    }
  } else {
    pageNotification.value = { title: t('info.invitationWasSentContext', { email: inviteEmail.value }) };
    inviteEmail.value = '';
    await refresh();
  }

  loading.value = false;
};

const amIAdmin = async () => {
  const response: BooleanResponse = await call('permission-check').post().json();
  const { error } = response;

  return !error.value;
};

const hardDeleteConfirm = async () => {
  if (!hardDeleteModalContext.value) {
    hardDeleteModalOpen.value = false;
    hardDeleteModalContext.value = null;
    return;
  }

  // Use ids here
  const response: BooleanResponse = await call(`subscriber/hard-delete/${hardDeleteModalContext.value}`).put().json();
  const { data } = response;

  if (data.value) {
    await refresh();
  }

  hardDeleteModalOpen.value = false;
  hardDeleteModalContext.value = null;
};

const onFieldClick = (_key: string, field: any) => {
  if (_key === 'disable') {
    toggleSubscriberState(field.email.value, field.timeDeleted.value === '');
  } else if (_key === 'hardDelete') {
    hardDeleteModalOpen.value = true;
    hardDeleteModalContext.value = field.id.value;
  }
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
      data-name="Subscribers"
      data-key="id"
      :allow-multi-select="false"
      :data-list="filteredSubscribers"
      :columns="columns"
      :filters="filters"
      :loading="loading"
      @field-click="onFieldClick"
    >
      <template v-slot:footer>
        <div class="flex w-full justify-between">
          <div class="flex w-1/3 flex-col gap-4 text-center md:w-full md:flex-row md:text-left">
            <label class="flex flex-col gap-4 md:flex-row md:items-center md:gap-0">
              <span>{{ t('label.enterEmailToInvite') }}</span>
              <input
                class="mx-4 w-60 rounded-md text-sm"
                type="email"
                placeholder="e.g. test@example.org"
                v-model="inviteEmail"
                :disabled="loading"
                enterkeyhint="send"
                @keyup.enter="sendInvite"
              />
            </label>
            <primary-button class="btn-send" :disabled="loading" @click="sendInvite" :title="t('label.send')">
              <icon-send/>
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
      </template>

    </data-table>
  </div>
  <div v-else class="flex size-full min-h-[75vh] items-center justify-center">
    <loading-spinner/>
  </div>
  <!-- Refresh link confirmation modal -->
  <confirmation-modal
    :open="hardDeleteModalOpen"
    title="WARNING"
    message="This will completely remove a user from Thunderbird Appointment, including all of their user data. Don't do this unless you're told to."
    confirm-label="Delete"
    :cancel-label="t('label.cancel')"
    :use-caution-button="true"
    @confirm="() => hardDeleteConfirm()"
    @close="hardDeleteModalOpen = false"
  ></confirmation-modal>
</template>
