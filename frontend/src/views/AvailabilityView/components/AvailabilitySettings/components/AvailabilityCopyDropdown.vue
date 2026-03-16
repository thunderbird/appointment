<script setup lang="ts">
import { inject, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { isoWeekdaysKey } from '@/keys';
import { CopyTemplate } from '@/models';
import { PhCopy } from '@phosphor-icons/vue';
import DropDown from '@/elements/DropDown.vue';
import ContainerBox from '@/elements/ContainerBox.vue';
import { CheckboxInput, LinkButton, PrimaryButton } from '@thunderbirdops/services-ui';

const { t } = useI18n();
const isoWeekdays = inject(isoWeekdaysKey);
const defaultSelection = Object.fromEntries(isoWeekdays.map((day) => [day.iso, false])) as CopyTemplate;

// component properties
interface Props {
  disabledWeekdays: number[]; // A list of weekdays that cannot be selected
}

const props = defineProps<Props>();

const emit = defineEmits(['copy']);

const selectedDays = ref(defaultSelection);
const allDaysSelected = ref(false);
const copyDropdown = ref();

const copy = () => {
  emit('copy', selectedDays.value);
  copyDropdown.value.close();
};


// Handle bulk checking all weekdays
watch(
  () => allDaysSelected.value,
  (value) => {
    Object.keys(selectedDays.value).forEach((k) => {
      selectedDays.value[Number(k)] = props.disabledWeekdays.includes(Number(k)) ? false : value;
    });
  },
);

</script>

<template>
  <drop-down class="drop-down-wrapper" ref="copyDropdown">
    <template #trigger>
      <link-button size="large" class="action-btn action-copy" :title="t('label.copyAvailability')">
        <ph-copy aria-hidden="true"/>
      </link-button>
    </template>
    <template #default>
      <container-box class="selection-container">
        <label>{{ t('label.copyTimesTo') }}</label>
        <checkbox-input name="all" :label="t('label.selectAll')" v-model="allDaysSelected" />
        <hr>
        <checkbox-input
          v-for="d in isoWeekdays"
          v-model="selectedDays[d.iso]"
          :key="d.iso"
          :value="d.iso"
          :name="d.short.toLowerCase()"
          :label="d.long"
          v-bind="disabledWeekdays.includes(d.iso) ? { disabled: true } : {}"
          :data-testid="`availability-copy-to-${d.long.toLowerCase()}-input`"
        />
        <hr>
        <primary-button @click="copy" :title="t('label.copyAvailability')">
          {{ t('label.apply') }}
        </primary-button>
      </container-box>
    </template>
  </drop-down>
</template>

<style scoped>
.drop-down-wrapper {
  align-self: center;
}

.selection-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  width: max-content;

  label {
    font-size: 1rem;
    font-weight: 600;
    color: var(--colour-ti-secondary);
  }

  :deep(.checkbox-wrapper) label{
    font-size: 0.875rem;
  }

  :deep(button) {
    padding-top: .625rem;
    padding-bottom: .625rem;
  }
}

.action-copy.base.link.filled {
  color: var(--colour-ti-base);
  padding: .25rem .125rem;
  width: 2rem;
  height: 2rem;

  svg { 
    width: 1.5rem;
    height: 1.5rem;
  }
}
</style>
