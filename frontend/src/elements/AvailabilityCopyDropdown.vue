<script setup lang="ts">
import { inject, ref, watch } from 'vue';
import { isoWeekdaysKey } from '@/keys';
import { CopyTemplate } from '@/models';
import { IconAsterisk } from '@tabler/icons-vue';
import DropDown from '@/elements/DropDown.vue';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import CheckboxInput from '@/tbpro/elements/CheckboxInput.vue';
import ContainerBox from '@/tbpro/elements/ContainerBox.vue';
import LinkButton from '@/tbpro/elements/LinkButton.vue';

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
  <drop-down class="self-center" ref="copyDropdown">
    <template #trigger>
      <link-button size="small" class="action-btn action-copy">
        <icon-asterisk class="w-4" aria-hidden="true"/>
      </link-button>
    </template>
    <template #default>
      <container-box class="flex flex-col gap-2">
        Copy to:
        <checkbox-input name="all" label="Select all" v-model="allDaysSelected" />
        <hr>
        <checkbox-input
          v-for="d in isoWeekdays"
          v-model="selectedDays[d.iso]"
          :key="d.iso"
          :value="d.iso"
          :name="d.short.toLowerCase()"
          :label="d.long"
          :disabled="disabledWeekdays.includes(d.iso)"
          :data-testid="`dashboard-availability-copy-to-${d.long.toLowerCase()}-input`"
        />
        <hr>
        <primary-button @click="copy">Apply</primary-button>
      </container-box>
    </template>
  </drop-down>
</template>

<style scoped>
.action-btn {
  padding: .25rem .125rem;
}
.action-copy {
  color: var(--colour-ti-secondary);
}
</style>
