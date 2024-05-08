<template>
  <!-- page title area -->
  <div v-if="user.exists()" class="flex flex-col items-center justify-center gap-4">
    <div class="flex flex-row justify-between items-center w-full">
      <div>
        <span class="font-bold">{{ filteredSubscribers.length }}</span> Subscribers
      </div>
      <list-pagination
        :list-length="filteredSubscribers.length"
        :page-size="pageSize"
        @update="updatePage"
      />
    </div>
    <div class="data-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Email</th>
            <th>Invite code used</th>
            <th>Time Created</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="subscriber in paginatedSubscribers" :key="subscriber.id">
            <td>
              <code>{{ subscriber.id }}</code>
            </td>
            <td>
              <code>{{ subscriber.username }}</code>
            </td>
            <td>
              {{ subscriber.email }}
            </td>
            <td>TODO</td>
            <td class="whitespace-nowrap">{{ dj(subscriber.time_created).format('ll LTS') }}</td>
            <td class="w-28 py-2">
              <!-- TODO -->
              <caution-button
                disabled
                :label="'Disable'"
                class="text-sm px-4 h-8"
                @click="disableSubscriber(subscriber.email)"
              />
            </td>
          </tr>
          <tr v-if="filteredSubscribers.length === 0">
            <td colspan="5">No subscribers could be found.</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <th colspan="6">
            </th>
          </tr>
        </tfoot>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, inject, onMounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useUserStore } from '@/stores/user-store';
import CautionButton from '@/elements/CautionButton.vue';
import ListPagination from '@/elements/ListPagination.vue';

// component constants
const user = useUserStore();
const call = inject('call');
const dj = inject('dayjs');

// component constants
const { t } = useI18n();

// pagination
const pageSize = 10;
const currentPage = ref(0);
const updatePage = (index) => {
  currentPage.value = index;
}

// subscriber specific props
const subscribers = ref([]);

const filteredSubscribers = computed(() => {
  let filtered = subscribers.value;

  return filtered;
});

const paginatedSubscribers = computed(() => {
  return filteredSubscribers.value.length
    ? filteredSubscribers.value.slice(currentPage.value*pageSize, (currentPage.value+1)*pageSize)
    : [];
});

const getSubscribers = async () => {
  const response = await call('subscriber/').get().json();
  const { data } = response;

  subscribers.value = data.value;
};

const disableSubscriber = async (email) => {
  if (!email) {
    return;
  }

  const response = await call(`subscriber/disable/${email}`).put().json();
  const { data } = response;

  if (data.value) {
    await getSubscribers();
  }
};

onMounted(async () => {
  await getSubscribers();
});

</script>
