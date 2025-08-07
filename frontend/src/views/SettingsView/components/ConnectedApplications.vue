<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { IconDots } from '@tabler/icons-vue';
import { PrimaryBadge, CheckboxInput, SecondaryButton } from '@thunderbirdops/services-ui';
import DropDown from '@/elements/DropDown.vue';

const { t } = useI18n();
const calendarDropdown = ref();
</script>

<template>
  <header>
    <h2>{{ t('label.connectedApplications') }}</h2>
  </header>

  <div class="form-field-container">
    <!-- Video Meeting -->
    <label class="form-field-label" for="videoMeeting">
      {{ t('label.videoMeeting') }}
    </label>

    <p>Connected as dnakano@email.com</p>
    <br />
    <p>Zoom</p>
    <icon-dots size="24" />

    <!-- Calendars -->
    <label class="form-field-label" for="calendars">
      {{ t('label.calendar', 2) }}
    </label>

    <div class="calendar-details-container">
      <checkbox-input
        name="calendarConnected"
        class="calendar-connected-checkbox"
      />
      <primary-badge>
        Default
      </primary-badge>
      <p>dnakano@email.com</p>
    </div>

    <div class="calendar-color"></div>
    <p>Google</p>

    <drop-down class="self-center" ref="calendarDropdown">
      <template #trigger>
        <icon-dots size="24" />
      </template>
      <template #default>
        <div @click="calendarDropdown.close()">
          <p>hey</p>
        </div>
      </template>
    </drop-down>
  </div>

  <div class="footer-buttons-container">
    <secondary-button>Add Google Calendar</secondary-button>
    <secondary-button>Add CalDav</secondary-button>
  </div>
</template>

<style scoped>
header {
  margin-block-end: 2rem;
}

h2 {
  font-size: 1.5rem;
}

.form-field-container {
  display: grid;
  grid-template-columns: 20% 2fr 24px 1fr 24px;
  grid-gap: 1.5rem;
  margin-block-end: 2rem;
}

.calendar-details-container {
  display: flex;
  align-items: center;
  gap: 1.5rem;

  .calendar-connected-checkbox {
    width: auto;
  }
}

.calendar-color {
  width: 24px;
  height: 24px;
  background-color: red;
}

.footer-buttons-container {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 1rem;
}
</style>