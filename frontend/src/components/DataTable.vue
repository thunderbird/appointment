<template>
<div class="flex flex-col items-center justify-center gap-4">
    <div class="flex w-full flex-row items-center justify-between">
      <div>
        <span class="font-bold">{{ paginatedDataList.length }}</span> {{ dataName }}
      </div>
      <div v-for="filter in filters" :key="filter.name">
        <label class="flex items-center gap-4 whitespace-nowrap">
        {{ filter.name }} {{ t('label.filter') }}:
        <select class="rounded-md" @change="(evt) => onColumnFilter(evt, filter)">
          <option :value="option.key" v-for="option in filter.options" :key="option.key">{{ option.name }}</option>
        </select>
        </label>
      </div>
      <list-pagination
        :list-length="dataList.length"
        :page-size="pageSize"
        @update="updatePage"
      />
    </div>
    <div class="data-table">
      <table>
        <thead>
          <tr>
            <th v-if="allowMultiSelect">
              <!-- Decide if we want to select all for the paginated list or all data -->
            </th>
            <th v-for="column in columns" :key="column.key">{{ column.name }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="datum in paginatedDataList" :key="datum">
            <td v-if="allowMultiSelect">
              <input type="checkbox" @change="(evt) => onFieldSelect(evt, datum)" />
            </td>
            <td v-for="(fieldData, fieldKey) in datum" :key="fieldKey">
              <span v-if="fieldData.type === tableDataType.text">
                {{ fieldData.value }}
              </span>
              <span v-else-if="fieldData.type === tableDataType.link">
                <a :href="fieldData.link" target="_blank">{{ fieldData.value }}</a>
              </span>
              <span v-else-if="fieldData.type === tableDataType.button">
                <primary-button v-if="fieldData.buttonType === tableDataButtonType.primary" @click="emit('fieldClick', fieldKey, datum)">{{ fieldData.value }}</primary-button>
                <secondary-button v-else-if="fieldData.buttonType === tableDataButtonType.secondary" @click="emit('fieldClick', fieldKey, datum)">{{ fieldData.value }}</secondary-button>
                <caution-button v-else-if="fieldData.buttonType === tableDataButtonType.caution" @click="emit('fieldClick', fieldKey, datum)">{{ fieldData.value }}</caution-button>
              </span>
            </td>
          </tr>
          <tr v-if="loading">
            <td :colspan="columnSpan">
              <div class="flex w-full justify-center">
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

<script setup>
/**
 * Data Table
 * @typedef {{type: tableDataType, value: string, link?: string, buttonType?: tableDataButtonType }} DataField
 * @typedef {{name: string, key: string}} DataColumn
 * @typedef {{name: string, key: string}} FilterOption
 * @typedef {{name: string, options: Array<FilterOption>, fn: function}} Filter
 *
 * @param allowMultiSelect {boolean} - Displays checkboxes next to each row, and emits the `fieldSelect` event with a list of currently selected rows
 * @param dataName {string} - The name for the object being represented on the table
 * @param columns {Array<DataColumn>} - List of columns to be displayed (these don't filter data, filter that yourself!)
 * @param dataList {Array<DataField>} - List of data to be displayed
 * @param filters {Array<Filter>} - List of filters to be displayed
 * @param loading {boolean} - Displays a loading spinner
 */
import ListPagination from '@/elements/ListPagination.vue';
import { useI18n } from 'vue-i18n';
import {
  computed, ref, toRefs,
} from 'vue';
import { tableDataButtonType, tableDataType } from '@/definitions';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import SecondaryButton from '@/elements/SecondaryButton.vue';
import CautionButton from '@/elements/CautionButton.vue';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';

const props = defineProps({
  allowMultiSelect: Boolean,
  dataName: String,
  dataList: Array,
  columns: Array,
  filters: Array,
  loading: Boolean,
});

const {
  dataList, columns, dataName, allowMultiSelect, loading,
} = toRefs(props);

const { t } = useI18n();
const emit = defineEmits(['fieldSelect', 'fieldClick']);

// pagination
const pageSize = 10;
const currentPage = ref(0);
const updatePage = (index) => {
  currentPage.value = index;
};

const columnSpan = computed(() => (columns.value.length + (allowMultiSelect.value ? 1 : 0)));
const selectedFields = ref([]);

const mutableDataList = ref([]);

/**
 * Returns either a filtered data list, or the original all nice and paginated
 */
const paginatedDataList = computed(() => {
  if (mutableDataList?.value?.length) {
    return mutableDataList.value.slice(currentPage.value * pageSize, (currentPage.value + 1) * pageSize);
  }
  if (dataList?.value?.length) {
    return dataList.value.slice(currentPage.value * pageSize, (currentPage.value + 1) * pageSize);
  }

  return [];
});

const onFieldSelect = (evt, fieldData) => {
  const isChecked = evt?.target?.checked;

  if (isChecked) {
    selectedFields.value.push(fieldData);
  } else {
    const index = selectedFields.value.indexOf(fieldData);
    if (index !== -1) {
      selectedFields.value.splice(index, 1);
    }
  }
  emit('fieldSelect', selectedFields.value);
};

const onColumnFilter = (evt, filter) => {
  mutableDataList.value = filter.fn(evt.target.value, dataList.value);
  if (mutableDataList.value === dataList.value) {
    mutableDataList.value = [];
  }
};

</script>
