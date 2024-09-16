<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { CalendarItem } from '@/models';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';

const { t } = useI18n();
const model = defineModel<CalendarItem[]>();

const selected = computed(() => model.value.filter((item) => item.checked).length);
const selectAll = () => {
  model.value = model.value.map((item) => ({
    ...item,
    checked: true,
  }));
};

// component properties
interface Props {
  title: string;
}
defineProps<Props>();
</script>

<template>
  <div class="wrapper">
    <div class="header">
      <slot name="icon"></slot>
      <div class="text-wrapper">
        <div class="title">
          {{ title }}
        </div>
        <div class="selected">
          {{ t('ftue.itemsSelected', {'count': selected}) }}
        </div>
      </div>
      <primary-button class="select-all" size="small" @click="selectAll" :title="t('ftue.selectAllCalendars')">
        {{ t('ftue.selectAll') }}
      </primary-button>
    </div>
    <ul class="rows">
      <li class="row" v-for="(item, index) in model" :key="item.key">
        <label>
          <input type="checkbox" v-model="model[index].checked"/>
          {{ item.label }}
        </label>
      </li>
    </ul>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.wrapper {
  --colour-highlight: var(--colour-service-primary);
  border-radius: 0.5625rem;
  border: 0.0625rem solid var(--colour-neutral-border);
  background: var(--colour-neutral-base);
  font-family: 'Inter', 'sans-serif';
  font-size: var(--txt-input);
  color: var(--colour-ti-base);
}

.dark {
  .wrapper {
    --colour-highlight: var(--colour-service-secondary);
  }
}

.header {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;

  position: relative;
  min-height: 3.375rem;
  gap: 0.5rem;
  padding: 0.75rem 0.625rem;
  border-top-left-radius: 0.5rem;
  border-top-right-radius: 0.5rem;
  border-bottom: 0.0625rem solid var(--colour-neutral-border);
  background-color: var(--colour-neutral-lower);
  font-weight: 700;
}

.selected {
  font-size: 0.5625rem;
  color: var(--colour-highlight);
}

.rows {
  height: 12.0rem;
  overflow-y: scroll;
  border-radius: 0.5rem;
}

.row {
  width: 100%;
  background-color: var(--colour-neutral-base);
  padding: 0.375rem 0.75rem;
  font-size: var(--txt-input);

  &:nth-child(even) {
    background-color: var(--colour-neutral-lower);
  }
}

label {
  display: flex;
  gap: 0.625rem;
  justify-content: flex-start;
  align-items: center;
}

input {
  width: 1.0rem;
  height: 1.0rem;
  border-radius: var(--border-radius);
  border: 1px solid var(--colour-neutral-border-intense);

  &:focus {
    outline-color: var(--colour-highlight);
  }

  &:checked, &:checked:hover, &:checked:focus {
    background-color: var(--colour-highlight);
    border-color: var(--colour-highlight);
    color: var(--colour-neutral-raised);
  }
}

.select-all {
  margin-left: auto;
  margin-right: auto;
  top: 2.0625rem;
}

@media (--md) {
  .header {
    flex-direction: row;
    justify-content: flex-start;
    align-items: flex-start;
    text-align: left;
  }
  .select-all {
    position: relative;
    margin-right: 0.25rem;
  }
}
</style>
