<script setup lang="ts">
import {
  computed, inject, onMounted, ref,
} from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import AlertBox from '@/elements/AlertBox.vue';
import DataTable from '@/components/DataTable.vue';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';
import ConfirmationModal from '@/components/ConfirmationModal.vue';
import { TextInput } from '@thunderbirdops/services-ui';
import { dayjsKey, callKey } from '@/keys';
import {
  Subscriber, BooleanResponse, Exception, TableDataRow, TableDataColumn, TableFilter, Alert,
} from '@/models';
import { useUserStore } from '@/stores/user-store';
import { AlertSchemes, TableDataButtonType, TableDataType } from '@/definitions';
import { staggerRetrieve } from '@/utils';

const user = useUserStore();

const router = useRouter();
const { t } = useI18n();

const call = inject(callKey);
const dj = inject(dayjsKey);

const subscribers = ref<Subscriber[]>([]);
const displayPage = ref(false);
const loading = ref(true);
const pageError = ref<Alert>(null);
const pageNotification = ref<Alert>(null);
const hardDeleteModalOpen = ref<boolean>(false);
const hardDeleteModalContext = ref<Subscriber>(null);
const emailFilter = ref<string>(null);
const subscriberList = computed(() => {
  if (emailFilter.value) {
    /** @ts-expect-error escape has no baseline support yet */
    return subscribers.value.filter((sub) => sub.email.match(new RegExp(RegExp.escape(emailFilter.value), 'gi')));
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
    value: subscriber.timezone ?? t('label.unset'),
  },
  disable: {
    type: TableDataType.Button,
    buttonType: subscriber.time_deleted ? TableDataButtonType.Primary : TableDataButtonType.Caution,
    value: subscriber.time_deleted ? t('label.enable') : t('label.disable'),
    disabled: !subscriber.time_deleted && subscriber.email === user.data.email,
  },
  hardDelete: {
    type: TableDataType.Button,
    buttonType: TableDataButtonType.Caution,
    value: t('label.hardDelete'),
    disabled: !subscriber.time_deleted || subscriber.email === user.data.email,
    tooltip: `${t('text.admin.completelyRemoveUser')} ${t('text.admin.disableAccountFirst')}`,
  },
} as TableDataRow)));
const columns = [
  {
    key: 'id',
    name: 'ID',
  },
  {
    key: 'username',
    name: t('label.username'),
  },
  {
    key: 'email',
    name: t('label.email'),
  },
  {
    key: 'createdAt',
    name: t('label.timeCreated'),
  },
  {
    key: 'deletedAt',
    name: t('label.timeDeleted'),
  },
  {
    key: 'timezone',
    name: t('label.timeZone'),
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
 * @param id
 * @param currentState True if currently enabled (= not deleted)
 */
const toggleSubscriberState = async (id: string, currentState: boolean) => {
  if (!id) {
    return;
  }

  const action = currentState ? 'disable' : 'enable';
  const response: BooleanResponse = await call(`subscriber/${action}/${id}`).put().json();
  const { data } = response;

  if (data.value) {
    await refresh();
  }
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
    toggleSubscriberState(field.id.value, field.timeDeleted.value === '');
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
  <div v-if="displayPage">
    <data-table
      :data-name="t('label.admin-subscriber-panel')"
      data-key="id"
      :allow-multi-select="false"
      :data-list="filteredSubscribers"
      :columns="columns"
      :loading="loading"
      @field-click="onFieldClick"
    >
      <template v-slot:footer>
        <text-input
          name="search"
          class="w-60"
          type="text"
          v-model="emailFilter"
          :disabled="loading"
          placeholder="Search"
        />
      </template>

    </data-table>
  </div>
  <div v-else class="flex size-full min-h-[75vh] items-center justify-center">
    <loading-spinner/>
  </div>
  <!-- Refresh link confirmation modal -->
  <confirmation-modal
    :open="hardDeleteModalOpen"
    :title="t('label.warning').toUpperCase()"
    :message="t('text.admin.completelyRemoveUser')"
    :confirm-label="t('label.delete')"
    :cancel-label="t('label.cancel')"
    :use-caution-button="true"
    @confirm="() => hardDeleteConfirm()"
    @close="hardDeleteModalOpen = false"
  ></confirmation-modal>
</template>
