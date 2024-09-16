<script setup lang="ts">
import {
  computed, inject, onMounted, ref,
} from 'vue';
import { useI18n } from 'vue-i18n';
import {
  AlertSchemes, TableDataButtonType, TableDataType, InviteStatus,
} from '@/definitions';
import { useRouter } from 'vue-router';
import { IconSend } from '@tabler/icons-vue';
import {
  Invite, InviteListResponse, BooleanResponse, Exception, TableDataRow, TableDataColumn, TableFilter,
} from '@/models';
import { dayjsKey, callKey } from '@/keys';
import DataTable from '@/components/DataTable.vue';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import AlertBox from '@/elements/AlertBox.vue';
import AdminNav from '@/elements/admin/AdminNav.vue';

const router = useRouter();
const { t } = useI18n();

const call = inject(callKey);
const dj = inject(dayjsKey);

const invites = ref<Invite[]>([]);
const displayPage = ref(false);
const generateCodeAmount = ref(null);
const loading = ref(true);
const pageError = ref('');
const pageNotification = ref('');

const filteredInvites = computed(() => invites.value.map((invite) => ({
  code: {
    type: TableDataType.Code,
    value: invite.code,
  },
  status: {
    type: TableDataType.Text,
    value: invite.status === InviteStatus.Active ? 'Available' : 'Revoked',
  },
  subscriber_id: {
    type: TableDataType.Text,
    value: invite.subscriber_id ?? 'Unused',
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
    value: 'Revoke',
    disabled: invite.subscriber_id || invite.status === InviteStatus.Revoked,
  },
} as TableDataRow)));
const columns = [
  {
    key: 'code',
    name: 'Code',
  },
  {
    key: 'status',
    name: 'Status',
  },
  {
    key: 'subscriber_id',
    name: 'Invited Subscriber ID',
  },
  {
    key: 'createdAt',
    name: 'Time Created',
  },
  {
    key: 'updatedAt',
    name: 'Time Updated',
  },
  {
    key: 'revoke',
    name: '',
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
        name: 'Used',
        key: 'used',
      },
      {
        name: 'Unused',
        key: 'unused',
      },
      {
        name: 'Revoked',
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
          return mutableDataList.filter((data) => (data.status.value === 'Revoked'));
        case 'used':
          return mutableDataList.filter((data) => {
            if (data.status.value === 'Revoked') {
              return false;
            }

            return data.subscriber_id.value !== 'Unused';
          });
        case 'unused':
          return mutableDataList.filter((data) => {
            if (data.status.value === 'Revoked') {
              return false;
            }

            return data.subscriber_id.value === 'Unused';
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
  const response: InviteListResponse = await call('invite/').get().json();
  const { data } = response;

  invites.value = data.value as Invite[];
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
  pageError.value = '';
  pageNotification.value = '';

  const response: InviteListResponse = await call(`invite/generate/${generateCodeAmount.value}`).post().json();

  const { data, error } = response;

  if (error.value) {
    const errorObj = (data.value as Exception)?.detail;

    if (!errorObj) {
      pageError.value = t('error.somethingWentWrong');
    } else if (errorObj instanceof Array) {
      pageError.value = errorObj.map((err) => err.msg).join('\n');
    } else {
      pageError.value = errorObj?.message;
    }
  } else {
    pageNotification.value = t('info.invitationGenerated');
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
    <alert-box v-if="pageNotification" @close="pageNotification = ''" :scheme="AlertSchemes.Success">
      {{ pageNotification }}
    </alert-box>
    <alert-box v-if="pageError" @close="pageError = ''">
      {{ pageError }}
    </alert-box>
  </div>
  <admin-nav/>
  <div v-if="displayPage">
    <data-table
      data-key="code"
      data-name="Invite Codes"
      :allow-multi-select="false"
      :data-list="filteredInvites"
      :columns="columns"
      :filters="filters"
      :loading="loading"
      @field-click="(_key, field) => revokeInvite(field.code.value)"
    >
      <template v-slot:footer>
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
      </template>

    </data-table>
  </div>
  <div v-else class="flex size-full min-h-[75vh] items-center justify-center">
    <loading-spinner/>
  </div>
</template>
