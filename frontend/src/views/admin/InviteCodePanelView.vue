<script setup lang="ts">
import {
  computed, inject, onMounted, ref,
} from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { IconSend } from '@tabler/icons-vue';
import DataTable from '@/components/DataTable.vue';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import AlertBox from '@/elements/AlertBox.vue';
import AdminNav from '@/elements/admin/AdminNav.vue';
import { dayjsKey, callKey } from '@/keys';
import {
  Invite, InviteListResponse, BooleanResponse, Exception, TableDataRow, TableDataColumn, TableFilter, Alert,
} from '@/models';
import {
  AlertSchemes, TableDataButtonType, TableDataType, InviteStatus,
} from '@/definitions';
import { staggerRetrieve } from '@/utils';

const router = useRouter();
const { t } = useI18n();

const call = inject(callKey);
const dj = inject(dayjsKey);

const invites = ref<Invite[]>([]);
const displayPage = ref(false);
const generateCodeAmount = ref(null);
const loading = ref(true);
const pageError = ref<Alert>(null);
const pageNotification = ref<Alert>(null);
const codeFilter = ref<string>(null);
const inviteList = computed(() => {
  if (codeFilter.value) {
    return invites.value.filter((invite) => invite.code.match(new RegExp(RegExp.escape(codeFilter.value), 'gi')));
  }
  return invites.value;
});

const filteredInvites = computed(() => inviteList.value.map((invite) => ({
  code: {
    type: TableDataType.Code,
    value: invite.code,
  },
  status: {
    type: TableDataType.Text,
    value: invite.status === InviteStatus.Active ? t('label.available') : t('label.revoked'),
  },
  subscriber_id: {
    type: TableDataType.Text,
    value: invite.subscriber_id ?? t('label.unused'),
  },
  timeCreated: {
    type: TableDataType.Text,
    value: dj(invite.time_created).format('ll LTS'),
  },
  timeUpdated: {
    type: TableDataType.Text,
    value: dj(invite.time_updated).format('ll LTS'),
  },
  revoke: {
    type: TableDataType.Button,
    buttonType: TableDataButtonType.Secondary,
    value: t('label.revoke'),
    disabled: invite.subscriber_id || invite.status === InviteStatus.Revoked,
  },
} as TableDataRow)));
const columns = [
  {
    key: 'code',
    name: t('label.code'),
  },
  {
    key: 'status',
    name: t('label.status'),
  },
  {
    key: 'subscriber_id',
    name: t('label.invitedSubscriberId'),
  },
  {
    key: 'createdAt',
    name: t('label.timeCreated'),
  },
  {
    key: 'updatedAt',
    name: t('label.timeUpdated'),
  },
  {
    key: 'revoke',
    name: '',
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
        name: t('label.used'),
        key: 'used',
      },
      {
        name: t('label.unused'),
        key: 'unused',
      },
      {
        name: t('label.revoked'),
        key: 'revoked',
      },
    ],
    /**
     * Callback function, filter the list by selectedKey and return it back to the table
     */
    fn: (selectedKey: string, mutableDataList: TableDataRow[]) => {
      switch (selectedKey) {
        case 'all':
          return null;
        case 'revoked':
          return mutableDataList.filter((data) => (data.status.value === t('label.revoked')));
        case 'used':
          return mutableDataList.filter((data) => {
            if (data.status.value === t('label.revoked')) {
              return false;
            }

            return data.subscriber_id.value !== t('label.unused');
          });
        case 'unused':
          return mutableDataList.filter((data) => {
            if (data.status.value === t('label.revoked')) {
              return false;
            }

            return data.subscriber_id.value === t('label.unused');
          });
        default:
          break;
      }
      return null;
    },
  },
] as TableFilter[];

/**
 * Retrieve list of all existing invites
 */
const getInvites = async () => {
  pageError.value = null;

  invites.value = await staggerRetrieve(
    (payload: object) => call('invite/').post(payload).json(),
    250,
    pageError,
  );
};

/**
 * Update list of all existing invites
 */
const refresh = async () => {
  loading.value = true;
  await getInvites();
  loading.value = false;
};

/**
 * Disables an unused invite
 * @param code Invitation identifier
 */
const revokeInvite = async (code: string) => {
  if (!code) {
    return;
  }

  const response: BooleanResponse = await call(`invite/revoke/${code}`).put().json();
  const { data } = response;

  if (data.value) {
    await refresh();
  }
};

const generateInvites = async () => {
  loading.value = true;
  pageError.value = null;
  pageNotification.value = null;

  const response: InviteListResponse = await call(`invite/generate/${generateCodeAmount.value}`).post().json();

  const { data, error } = response;

  if (error.value) {
    const errorObj = (data.value as Exception)?.detail;

    if (!errorObj) {
      pageError.value = { title: t('error.somethingWentWrong') };
    } else if (errorObj instanceof Array) {
      pageError.value = { title: errorObj.map((err) => err.msg).join('\n') };
    } else {
      pageError.value = { title: errorObj?.message };
    }
  } else {
    pageNotification.value = { title: t('info.invitationGenerated') };
    generateCodeAmount.value = null;
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
      data-key="code"
      :data-name="t('label.inviteCode', filteredInvites?.length)"
      :allow-multi-select="false"
      :data-list="filteredInvites"
      :columns="columns"
      :filters="filters"
      :loading="loading"
      @field-click="(_key, field) => revokeInvite(field.code.value)"
    >
      <template v-slot:footer>
        <div class="flex w-full justify-between">
          <div class="flex w-1/3 flex-col gap-4 text-center md:w-full md:flex-row md:text-left">
            <label class="flex flex-col gap-4 md:flex-row md:items-center md:gap-0">
              <span>{{ t('label.amountOfCodes') }}</span>
              <input
                class="mx-4 w-60 rounded-md text-sm"
                type="number"
                v-model="generateCodeAmount"
                :disabled="loading"
                enterkeyhint="done"
                @keyup.enter="generateInvites"
              />
            </label>
            <primary-button
              class="btn-generate"
              :disabled="loading"
              @click="generateInvites"
              :title="t('label.generate')"
            >
              <icon-send/>
              {{ t('label.generate') }}
            </primary-button>
          </div>
          <div class="flex flex-col items-end gap-4">
            <label class="flex flex-col gap-4 md:flex-row md:items-center md:gap-0">
              <span>{{ t('label.search') }}</span>
              <input
                class="mx-4 w-60 rounded-md text-sm"
                type="text"
                v-model="codeFilter"
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
</template>
