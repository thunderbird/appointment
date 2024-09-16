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
] as TableDataColumn[];

/**
 * Retrieve list of all existing invites
 */
const getInvites = async () => {
  const response: InviteListResponse = await call('me/invites').get().json();
  const { data } = response;

  invites.value = data.value as Invite[];
};

onMounted(async () => {
  await getInvites();
  loading.value = false;
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
  <div>
    <data-table
      data-key="code"
      data-name="Invite Codes"
      :allow-multi-select="false"
      :data-list="filteredInvites"
      :columns="columns"
      :loading="loading"
      :show-pagination="false"
    >
    </data-table>
  </div>
</template>
