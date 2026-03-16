<script setup lang="ts">
/**
 * Data Table
 */
import { useI18n } from 'vue-i18n';
import { computed, ref, toRefs } from 'vue';
import { TableDataButtonType, TableDataType } from '@/definitions';
import {
  TableDataRow, TableDataColumn, TableFilter, HTMLInputElementEvent,
} from '@/models';
import ListPagination from '@/elements/ListPagination.vue';
import { PrimaryButton, DangerButton } from '@thunderbirdops/services-ui';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';

// component properties
interface Props {
  allowMultiSelect: boolean, // Displays checkboxes next to each row, and emits the `fieldSelect` event with a list of currently selected rows
  dataName: string, // The name for the object being represented on the table
  dataKey: string, // A property to use as the list key
  columns: TableDataColumn[], // List of columns to be displayed (these don't filter data, filter that yourself!)
  dataList: TableDataRow[], // List of data to be displayed
  filters?: TableFilter[], // List of filters to be displayed
  loading: boolean, // Displays a loading spinner
  showPagination?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  filters: null,
  showPagination: true,
});

const {
  dataList, dataKey, columns, dataName, allowMultiSelect, loading,
} = toRefs(props);

const { t } = useI18n();
const emit = defineEmits(['fieldSelect', 'fieldClick']);

// pagination
const pageSize = 10;
const currentPage = ref(0);
const updatePage = (index: number) => {
  currentPage.value = index;
};

const columnSpan = computed(() => (columns.value.length + (allowMultiSelect.value ? 1 : 0)));
const selectedRows = ref<TableDataRow[]>([]);
const mutableDataList = ref<TableDataRow[]>(null);
const selectedFilters = {};

const clearSelectedRows = () => {
  selectedRows.value = [];
};

defineExpose({
  clearSelectedRows,
});

/**
 * Returns either a filtered data list, or the original all nice and paginated
 */
const paginatedDataList = computed(() => {
  if (mutableDataList?.value !== null) {
    return mutableDataList.value.slice(currentPage.value * pageSize, (currentPage.value + 1) * pageSize);
  }
  if (dataList?.value?.length) {
    return dataList.value.slice(currentPage.value * pageSize, (currentPage.value + 1) * pageSize);
  }

  return [];
});

const totalDataLength = computed(() => {
  if (mutableDataList?.value !== null) {
    return mutableDataList.value?.length ?? 0;
  }
  if (dataList?.value?.length) {
    return dataList.value.length;
  }
  return 0;
});

const onPageSelect = (evt: Event, list: TableDataRow[]) => {
  const target = evt.target as HTMLInputElement;
  const isChecked = target.checked;

  list.forEach((row) => {
    const index = selectedRows.value.indexOf(row);

    // Add and we're already in? OR Remove and we're not in? Skip!
    if ((isChecked && index !== -1) || (!isChecked && index === -1)) {
      return;
    }

    if (isChecked) {
      selectedRows.value.push(row);
    } else {
      selectedRows.value.splice(index, 1);
    }
  });

  emit('fieldSelect', selectedRows.value);
};

const onFieldSelect = (evt: Event, row: TableDataRow) => {
  const isChecked = (evt as HTMLInputElementEvent)?.target?.checked;

  if (isChecked) {
    selectedRows.value.push(row);
  } else {
    const index = selectedRows.value.indexOf(row);
    if (index !== -1) {
      selectedRows.value.splice(index, 1);
    }
  }
  emit('fieldSelect', selectedRows.value);
};

const onColumnFilter = (evt: Event, eventFilter: TableFilter, filters: TableFilter[]) => {
  mutableDataList.value = dataList.value;
  selectedFilters[eventFilter.name] = (evt as HTMLInputElementEvent).target.value;

  // We need to loop through all filters to re-apply them on filter change
  filters.forEach((filter: TableFilter) => {
    if (mutableDataList.value === null || !(filter.name in selectedFilters)) {
      return;
    }

    // The normal convention is to return null if we don't want to filter
    // So only apply the results if we're not null.
    const filteredDataList = filter.fn(selectedFilters[filter.name], mutableDataList.value);
    if (filteredDataList !== null) {
      mutableDataList.value = filteredDataList;
    }
  });

  if (mutableDataList.value === dataList.value) {
    mutableDataList.value = null;
  }
};

</script>

<template>
  <div class="table-wrapper">
    <div class="table-filter">
      <div>
        <strong>{{ totalDataLength }}</strong> {{ dataName }}
      </div>
      <div v-for="filter in filters" :key="filter.name">
        <label class="filter-item">
          {{ filter.name }} {{ t('label.filter') }}:
          <select @change="(evt) => onColumnFilter(evt, filter, filters)">
            <option :value="option.key" v-for="option in filter.options" :key="option.key">
              {{ option.name }}
            </option>
          </select>
        </label>
      </div>
      <list-pagination
        v-if="showPagination"
        :list-length="totalDataLength"
        :page-size="pageSize"
        @update="updatePage"
      />
    </div>
    <div class="data-table">
      <table>
        <thead>
          <tr>
            <th v-if="allowMultiSelect" class="multi-select-header">
              <input
                :checked="paginatedDataList.every((row) => selectedRows.includes(row))"
                @change="(evt) => onPageSelect(evt, paginatedDataList)"
                id="select-page-input"
                type="checkbox"
              />
              <label for="select-page-input">
                Select Page
              </label>
            </th>
            <th v-for="column in columns" :key="column.key">{{ column.name }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(datum) in paginatedDataList" :key="datum[dataKey] as unknown as string">
            <td v-if="allowMultiSelect">
              <input :checked="selectedRows.includes(datum)" type="checkbox" @change="(evt) => onFieldSelect(evt, datum)" />
            </td>
            <td v-for="(fieldData, fieldKey) in datum" :key="fieldKey" :class="`column-${fieldKey}`">
              <span v-if="fieldData.type === TableDataType.Text">
                {{ fieldData.value }}
              </span>
              <span v-else-if="fieldData.type === TableDataType.Code">
                <code>{{ fieldData.value }}</code>
              </span>
              <span v-else-if="fieldData.type === TableDataType.Bool">
                <span v-if="fieldData.value">{{ t('label.yes') }}</span>
                <span v-else>{{ t('label.no') }}</span>
              </span>
              <span v-else-if="fieldData.type === TableDataType.Link">
                <a :href="fieldData.link" target="_blank">{{ fieldData.value }}</a>
              </span>
              <span v-else-if="fieldData.type === TableDataType.Button">
                <primary-button
                  v-if="fieldData.buttonType === TableDataButtonType.Primary"
                  :disabled="fieldData.disabled"
                  :title="fieldData?.tooltip"
                  @click="emit('fieldClick', fieldKey, datum)"
                >
                  {{ fieldData.value }}
                </primary-button>
                <primary-button
                  v-else-if="fieldData.buttonType === TableDataButtonType.Secondary"
                  variant="outline"
                  :disabled="fieldData.disabled"
                  :title="fieldData?.tooltip"
                  @click="emit('fieldClick', fieldKey, datum)"
                >
                  {{ fieldData.value }}
                </primary-button>
                <danger-button
                  v-else-if="fieldData.buttonType === TableDataButtonType.Caution"
                  :disabled="fieldData.disabled"
                  :title="fieldData?.tooltip"
                  @click="emit('fieldClick', fieldKey, datum)"
                >
                  {{ fieldData.value }}
                </danger-button>
              </span>
            </td>
          </tr>
          <tr v-if="loading">
            <td :colspan="columnSpan" class="loading">
              <div>
                <loading-spinner/>
              </div>
            </td>
          </tr>
          <tr v-else-if="paginatedDataList.length === 0">
            <td :colspan="columnSpan">{{ t('error.dataSourceIsEmpty', {name: dataName}) }}</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <th :colspan="columnSpan">
              <slot name="footer"></slot>
            </th>
          </tr>
        </tfoot>
      </table>
    </div>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.table-wrapper {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 1rem;

  .table-filter {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;

    width: 100%;

    .filter-item {
      display: flex;
      align-items: center;
      gap: 1rem;
      white-space: nowrap;

      select {
        border-radius: 0.375rem
      }
    }
  }

  .data-table {
    overflow-x: auto;

    .multi-select-header {
      input {
        margin-right: 0.5rem;
      }
      label {
        cursor: pointer;
        user-select: none;
      }
    }

    td.column-code span {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    td.loading div {
      display: flex;
      width: 100%;
      justify-content: center;
    }
  }
}

@media (--md) {
  .table-wrapper {
    .table-filter {
      flex-direction: row;
      gap: 0;
    }
  }
}
</style>
