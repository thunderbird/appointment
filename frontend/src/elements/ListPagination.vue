<template>
  <nav class="flex items-center flex-nowrap gap-2" :class="{ 'hidden': !listLength }">
    <button @click="prev" :disabled="isFirstPage" :class="{ 'text-gray-500': isFirstPage }">
      <icon-chevron-left class="w-5 h-5 stroke-1.5" />
    </button>
    <div
      v-for="(p, i) in pageCount" :key="i"
      v-show="showPageItem(p)"
    >
      <div v-show="showFirstEllipsis(p)">&hellip;</div>
      <button
        class="cursor-pointer px-2 py-1"
        :class="{ 'text-gray-500': (p-1) == currentPage }"
        v-show="showPageItemLink(p)"
        @click="goto(p-1)"
      >
        {{ p }}
      </button>
      <div v-show="showLastEllipsis(p)">&hellip;</div>
    </div>
    <button @click="next" :disabled="isLastPage" :class="{ 'text-gray-500': isLastPage }">
      <icon-chevron-right class="w-5 h-5 stroke-1.5" />
    </button>
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';

// icons
import { IconChevronLeft, IconChevronRight } from '@tabler/icons-vue';

// component constants
const { t } = useI18n();

// component properties and emits
const props = defineProps({
  listLength: Number, // number of total items in the displayed list
  pageSize: Number, // number of items per page
});
const emit = defineEmits(['update'])

const currentPage = ref(0); // index of active page

const isFirstPage = computed(() => {
	return currentPage.value <= 0;
});
const pageCount = computed(() => {
	return Math.ceil(props.listLength/props.pageSize);
});
const isLastPage = computed(() => {
	return currentPage.value >= pageCount.value-1;
});

const prev = () => {
  if (!isFirstPage.value) {
    currentPage.value--;
    emit('update', currentPage.value);
  }
};
const next = () => {
  if (!isLastPage.value) {
    currentPage.value++;
    emit('update', currentPage.value);
  }
};
const goto = (index) => {
  currentPage.value = index;
  emit('update', currentPage.value);
};

const showPageItem = (p) => {
	return pageCount.value < 6 || p == 1 || p == 2 || isVisibleInnerPage(p) || p == pageCount.value-1;
};
const showFirstEllipsis = (p) => {
	return pageCount.value >= 6 && currentPage.value > 2 && p == 2;
};
const showPageItemLink = (p) => {
	return pageCount.value < 6 || p == 1 || isVisibleInnerPage(p);
};
const showLastEllipsis = (p) => {
	return pageCount.value >= 6 && currentPage.value < pageCount.value-3 && p == pageCount.value-1;
};

const isVisibleInnerPage = (p) => (currentPage.value == 0 && p == 3)
		|| ((currentPage.value == 0 || currentPage.value == 1) && p == 4)
		|| (p > currentPage.value-1 && p < currentPage.value+3)
		|| ((currentPage.value == pageCount.value-1 || currentPage.value == pageCount.value-2) && p == pageCount.value-3)
		|| (currentPage.value == pageCount.value-1 && p == pageCount.value-2)
    || p == pageCount.value;
</script>
