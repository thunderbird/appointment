<script setup lang="ts">
import { Alert } from '@/models';
import { AlertSchemes } from '@/definitions';
import { IconX } from '@tabler/icons-vue';
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { NoticeBar, NoticeBarTypes } from '@thunderbirdops/services-ui';

const { t } = useI18n();

// component properties
interface Props {
  alert: Alert; // Heading and optional description for the alert. If exists, the description is togglable.
  canClose?: boolean; // True if the alert can be closed / removed
  scheme?: AlertSchemes; // Type of the alert
}
const props = withDefaults(defineProps<Props>(), {
  canClose: true,
  scheme: AlertSchemes.Error,
});

const emit = defineEmits(['close']);

const hasDetails = Boolean(props.alert.details);

const alertSchemeToNoticeBarType = computed(() => {
  return {
    [AlertSchemes.Info]: NoticeBarTypes.Info,
    [AlertSchemes.Error]: NoticeBarTypes.Critical,
    [AlertSchemes.Success]: NoticeBarTypes.Success,
    [AlertSchemes.Warning]: NoticeBarTypes.Warning
  }
})

const open = ref(false);
const toggleDetails = () => {
  open.value = !open.value;
};
</script>

<template>
  <notice-bar :type="alertSchemeToNoticeBarType[props.scheme]">
    <span class="body">
      <span class="title">
        {{ alert.title }}
      </span>
      <span v-if="hasDetails && open">
        {{ alert.details }}
      </span>
    </span>

    <template #cta>
      <span class="controls">
        <span v-if="hasDetails" @click="toggleDetails" class="btn-toggle">
          <span v-if="open">Show less</span>
          <span v-if="!open">Show more</span>
        </span>
        <span v-if="canClose" class="btn-close" @click="emit('close')" :title="t('label.close')">
          <icon-x />
        </span>
      </span>
    </template>
  </notice-bar>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.icon {
  position: absolute;
  left: 0.5625rem;
  top: 0.75rem;
}
.body {
  margin: auto;
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  font-size: 0.8125rem;
}

.controls {
  display: flex;
  gap: 1rem;

  .btn-toggle {
    font-size: 0.8125rem;
    text-decoration-line: underline;
    text-underline-offset: 2px;
    cursor: pointer;
  }
  .btn-close {
    cursor: pointer;

    svg {
      stroke: currentColor;
      stroke-width: 1.5;
      width: 1rem;
    }
  }
}
</style>
