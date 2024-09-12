<script setup lang="ts">
import {
  onMounted, inject, ref, toRefs, onUnmounted,
} from 'vue';
import { refreshKey } from '@/keys';
import NoticeBar from '@/tbpro/elements/NoticeBar.vue';

// component properties
interface Props {
  infoMessage?: string;
  warningMessage?: string;
  errorMessage?: string;
}
const props = withDefaults(defineProps<Props>(), {
  infoMessage: null,
  warningMessage: null,
  errorMessage: null,
});

const { infoMessage, warningMessage, errorMessage } = toRefs(props);

const refresh = inject(refreshKey);

onMounted(async () => {
  // Activate page scroll-lock
  window.document.body.classList.add('modal-active');
  await refresh();
});
onUnmounted(() => {
  // Release page scroll-lock
  window.document.body.classList.remove('modal-active');
});
</script>

<template>
  <div class="new-design overlay" role="dialog" tabindex="-1" aria-labelledby="title" aria-modal="true">
    <div class="modal">
        <div class="modal-header">
          <slot name="header"></slot>
          <notice-bar type="error" v-if="errorMessage">
            {{ errorMessage }}
          </notice-bar>
          <notice-bar type="warning" v-else-if="warningMessage">
            {{ warningMessage }}
          </notice-bar>
          <notice-bar v-else-if="infoMessage">
            {{ infoMessage }}
          </notice-bar>
          <div class="pls-keep-height" v-else/>
        </div>
        <div class="modal-body">
          <slot></slot>
        </div>
        <div class="modal-actions">
          <slot name="actions"></slot>
        </div>
        <div class="divider"></div>
        <div class="footer">
          <slot name="footer"></slot>
        </div>
      </div>
  </div>
</template>
<style scoped>
@import '@/assets/styles/custom-media.pcss';
@import '@/assets/styles/mixins.pcss';

.overlay {
  @mixin faded-background var(--colour-shark-900);
  position: fixed;
  display: flex;
  left: 0;
  top: 0;
  z-index: 55;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  align-items: center;
  justify-content: center;
}

.modal-body {
  display: flex;
  width: 100%;
  flex-direction: column;
  align-items: center;
}

.modal-actions {
  display: flex;
  width: 100%;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

.modal-header {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 8.0rem;
  width: 100%;
  gap: 1rem;
}

/* Empty space if a notice bar isn't shown */
.pls-keep-height {
  min-height: 2.0625rem; /* 33px */
}

/* position-center apmt-background-color fixed z-[60] flex size-full gap-6 rounded-xl bg-white p-8 pb-0 drop-shadow-xl*/
.modal {
  --background-color: var(--colour-neutral-raised);
  --background: url('@/assets/svg/ftue-background.svg');
  position: relative;
  width: 100%;
  height: 100%;
  background-color: var(--background-color);
  background-image: var(--background);
  background-size: cover;
  background-repeat: no-repeat;
  border-radius: 0.75rem;
  padding: 1rem 1rem 0;
  overflow-y: scroll;
  overflow-x: hidden;
}

.dark .modal {
  --background: url('@/assets/svg/ftue-background-dark.svg');
}

.modal::before {
  content: '';
  position: absolute;
  inset: -4px;
  margin: 50% 5% 0;
  opacity: 0.8;
  z-index: -1;
  border-radius: 9px;
  background: linear-gradient(119deg, #A3ECE3 -1.91%, #03AFD7 48.8%, #008080 100.54%);
  filter: blur(30px);
}

.dark {
  .modal::before {
    background: linear-gradient(119deg, #0B8C86 -1.91%, #1C6395 100.54%);
  }
}

.divider {
  width: 100%;
  height: 0.0625rem;
  padding-bottom: 1px;
  border-radius: unset;
  margin-top: 2rem;
  margin-bottom: 1rem;
  background: linear-gradient(90deg, rgba(21, 66, 124, 0) 20.5%, rgba(21, 66, 124, 0.2) 50%, rgba(21, 66, 124, 0) 79.5%);
}
.dark {
  .divider {
    background: linear-gradient(90deg, rgba(255, 255, 255, 0.00) 0%, rgba(255, 255, 255, 0.40) 50%, rgba(255, 255, 255, 0.00) 100%);
  }
}

.footer {
  bottom: 0;
  height: 4rem;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding-bottom: 1rem;
  gap: 1rem;

  :deep(a) {
    color: var(--colour-service-primary-pressed);
    font-size: 0.75rem;
    line-height: 1.5rem;
  }
}

/* Default styling for #title */
:deep(#title) {
  color: var(--colour-ti-base);
  font-family: 'Inter', 'sans-serif';
  font-weight: 400;
  font-size: 1.375rem;
  line-height: 1.664rem;
}

@media (--md) {
  .modal-header {
    margin-bottom: 0;
  }

  .modal {
    width: 50rem; /* 800px */
    height: 37.5rem; /* 600px */
    padding: 2rem 2rem 0;
    overflow: visible;
  }

  .modal-body {
    height: 15.0rem;
  }

  .modal-actions {
    justify-content: center;
    position: absolute;
    left: 0;
    bottom: 5.75rem;
    margin: 0;
  }

  .divider {
    position: absolute;
    bottom: 4rem;
    width: 50rem;
    margin: 0;
  }

  .footer {
    position: absolute;
    left: 0;
    padding-bottom: 0;
  }
}

</style>
