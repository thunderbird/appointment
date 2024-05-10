<template>
  <div class="flex w-full justify-center">
    <alert-box
      @close="pageNotification = ''"
      v-if="pageNotification"
      :scheme="alertSchemes.success"
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
  <div v-if="displayPage">
    <data-table
    data-name="Subscribers"
    :allow-multi-select="false"
    :data-list="filteredSubscribers"
    :columns="columns"
    :filters="filters"
    :loading="loading"
    @field-click="(_key, field) => disableSubscriber(field.email.value)"
    >
      <template v-slot:footer>
        <div class="flex w-full gap-4">
          <label>
            {{ t('label.enterEmailToInvite') }}
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
          <primary-button :disabled="loading" @click="sendInvite">
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

<script setup>
import {
  computed, inject, onMounted, ref,
} from 'vue';
import { useI18n } from 'vue-i18n';
import { alertSchemes, tableDataButtonType, tableDataType } from '@/definitions';
import DataTable from '@/components/DataTable.vue';
import { useRouter } from 'vue-router';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import { IconSend } from '@tabler/icons-vue';
import AlertBox from '@/elements/AlertBox.vue';

const router = useRouter();
const { t } = useI18n();

const call = inject('call');
const dj = inject('dayjs');

const subscribers = ref([]);
const displayPage = ref(false);
const inviteEmail = ref('');
const loading = ref(true);
const pageError = ref('');
const pageNotification = ref('');

const filteredSubscribers = computed(() => subscribers.value.map((subscriber) => ({
  id: {
    type: tableDataType.text,
    value: subscriber.id,
  },
  username: {
    type: tableDataType.text,
    value: subscriber.username,
  },
  email: {
    type: tableDataType.text,
    value: subscriber.email,
  },
  timeCreated: {
    type: tableDataType.text,
    value: dj(subscriber.time_created).format('ll LTS'),
  },
  wasInvited: {
    type: tableDataType.text,
    value: subscriber.invite ? 'Yes' : 'No',
  },
  /*
  disable: {
    type: tableDataType.button,
    buttonType: tableDataButtonType.caution,
    value: 'Disable',
  },
   */
})));
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
    key: 'wasInvited',
    name: 'Was Invited?',
  },
  /*
  {
    key: 'disable',
    name: '',
  },
   */
];
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
        key: 'yes',
      },
      {
        name: 'No',
        key: 'no',
      },
    ],
    /**
     * Callback function, filter the list by selectedKey and return it back to the table
     * @param selectedKey
     * @param mutableDataList
     * @returns {*}
     */
    fn: (selectedKey, mutableDataList) => {
      if (selectedKey === 'all') {
        return mutableDataList;
      }
      return mutableDataList.filter((data) => data.wasInvited.value.toLowerCase() === selectedKey);
    },
  },
];
const getSubscribers = async () => {
  const response = await call('subscriber/').get().json();
  const { data } = response;

  subscribers.value = data.value;
};

const refresh = async () => {
  loading.value = true;
  await getSubscribers();
  loading.value = false;
};

/**
 * Disables a subscriber
 * @param email
 * @returns {Promise<void>}
 */
const disableSubscriber = async (email) => {
  if (!email) {
    return;
  }

  const response = await call(`subscriber/disable/${email}`).put().json();
  const { data } = response;

  if (data.value) {
    await refresh();
  }
};

const sendInvite = async () => {
  loading.value = true;
  pageError.value = '';
  pageNotification.value = '';

  const response = await call('invite/send').post({
    email: inviteEmail.value,
  }).json();

  const { data, error } = response;

  if (error.value) {
    const errorObj = data.value?.detail;

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
  const response = await call('permission-check').post().json();
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
