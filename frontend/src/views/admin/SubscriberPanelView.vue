<script setup lang="ts">
import { AlertSchemes, TableDataButtonType, TableDataType } from '@/definitions';
import {
  computed, inject, onMounted, ref,
} from 'vue';
import { IconSend } from '@tabler/icons-vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user-store';
import { Subscriber, SubscriberListResponse, BooleanResponse, Exception, TableDataRow, TableDataColumn, TableFilter } from "@/models";
import { dayjsKey, callKey } from "@/keys";
import AdminNav from '@/elements/admin/AdminNav.vue';
import AlertBox from '@/elements/AlertBox.vue';
import DataTable from '@/components/DataTable.vue';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';

const user = useUserStore();

const router = useRouter();
const { t } = useI18n();

const call = inject(callKey);
const dj = inject(dayjsKey);

const subscribers = ref<Subscriber[]>([]);
const displayPage = ref(false);
const inviteEmail = ref('');
const loading = ref(true);
const pageError = ref('');
const pageNotification = ref('');

const filteredSubscribers = computed(() => subscribers.value.map((subscriber) => ({
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
  const response: SubscriberListResponse = await call('subscriber/').get().json();
  const { data } = response;

  subscribers.value = data.value as Subscriber[];
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
  pageError.value = '';
  pageNotification.value = '';

  const response = await call('invite/send').post({
    email: inviteEmail.value,
  }).json();

  const { data, error } = response;

  if (error.value) {
    const errorObj = (data.value as Exception)?.detail;

    if (!errorObj) {
      pageError.value = t('error.somethingWentWrong');
    } else if (errorObj instanceof Array) {
      pageError.value = errorObj.map((err) => err.msg).join('\n');
    } else {
      pageError.value = data.value?.detail?.message;
    }
  } else {
    pageNotification.value = t('info.invitationWasSentContext', { email: inviteEmail.value });
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
      data-name="Subscribers"
      data-key="id"
      :allow-multi-select="false"
      :data-list="filteredSubscribers"
      :columns="columns"
      :filters="filters"
      :loading="loading"
      @field-click="(_key, field) => toggleSubscriberState(field.email.value, field.timeDeleted.value === '')"
    >
      <template v-slot:footer>
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
            <icon-send />
            {{ t('label.send') }}
          </primary-button>
        </div>
      </template>

    </data-table>
  </div>
  <div v-else class="flex size-full min-h-[75vh] items-center justify-center">
    <loading-spinner/>
  </div>
</template>
