<script setup lang="ts">
import {
  computed, inject, onMounted, ref,
} from 'vue';
import {
  AlertSchemes, TableDataType, InviteStatus,
} from '@/definitions';
import {
  Invite, InviteListResponse, TableDataRow, TableDataColumn,
} from '@/models';
import { callKey } from '@/keys';
import DataTable from '@/components/DataTable.vue';
import AlertBox from '@/elements/AlertBox.vue';

const call = inject(callKey);

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
    <alert-box
      v-if="pageNotification"
      :title="pageNotification"
      :scheme="AlertSchemes.Success"
      @close="pageNotification = ''"
    />
    <alert-box
      v-if="pageError"
      :title="pageError"
      @close="pageError = ''"
    />
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
