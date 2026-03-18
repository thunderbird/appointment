<script setup lang="ts">
import { ref, computed } from 'vue';

// icons
import { PhCaretLeft, PhCaretRight } from '@phosphor-icons/vue';

// component properties and emits
interface Props {
  listLength: number; // number of total items in the displayed list
  pageSize: number; // number of items per page
}
const props = defineProps<Props>();

const emit = defineEmits(['update']);

const currentPage = ref(0); // index of active page

const isFirstPage = computed(() => currentPage.value <= 0);
const pageCount = computed(() => Math.ceil(props.listLength / props.pageSize) || 1);
const isLastPage = computed(() => currentPage.value >= pageCount.value - 1);

const prev = () => {
  if (!isFirstPage.value) {
    currentPage.value -= 1;
    emit('update', currentPage.value);
  }
};
const next = () => {
  if (!isLastPage.value) {
    currentPage.value += 1;
    emit('update', currentPage.value);
  }
};
const goto = (index: number) => {
  currentPage.value = index;
  emit('update', currentPage.value);
};

const isVisibleInnerPage = (p: number) => (currentPage.value === 0 && p === 3)
    || ((currentPage.value === 0 || currentPage.value === 1) && p === 4)
    || (p > currentPage.value - 1 && p < currentPage.value + 3)
    || ((currentPage.value === pageCount.value - 1 || currentPage.value === pageCount.value - 2) && p === pageCount.value - 3)
    || (currentPage.value === pageCount.value - 1 && p === pageCount.value - 2)
    || p === pageCount.value;

const showPageItem = (p: number) => pageCount.value < 6 || p === 1 || p === 2 || isVisibleInnerPage(p) || p === pageCount.value - 1;
const showFirstEllipsis = (p: number) => pageCount.value >= 6 && currentPage.value > 2 && p === 2;
const showPageItemLink = (p: number) => pageCount.value < 6 || p === 1 || isVisibleInnerPage(p);
const showLastEllipsis = (p: number) => pageCount.value >= 6 && currentPage.value < pageCount.value - 3 && p === pageCount.value - 1;
</script>

<template>
  <nav class="pagination">
    <button @click="prev" :disabled="isFirstPage" class="btn-back" :class="{ 'disabled': isFirstPage }">
      <ph-caret-left :size="20" />
    </button>
    <div
      v-for="(p, i) in pageCount" :key="i"
      v-show="showPageItem(p)"
    >
      <div v-show="showFirstEllipsis(p)">&hellip;</div>
      <button
        class="btn-jump"
        :class="{ 'disabled': (p-1) === currentPage }"
        v-show="showPageItemLink(p)"
        @click="goto(p-1)"
      >
        {{ p }}
      </button>
      <div v-show="showLastEllipsis(p)">&hellip;</div>
    </div>
    <button @click="next" :disabled="isLastPage" class="btn-forward" :class="{ 'disabled': isLastPage }">
      <ph-caret-right :size="20" />
    </button>
  </nav>
</template>

<style scoped>
.pagination {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: .5rem;

  button {
    cursor: pointer;

    &.btn-jump {
      padding: .25rem .5rem;
    }

    &.disabled {
      cursor: default;
      color: var(--colour-ti-muted);
    }
  }
}
</style>
