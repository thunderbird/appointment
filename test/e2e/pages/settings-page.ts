import { type Page, type Locator } from '@playwright/test';

import {
  APPT_SETTINGS_PAGE,
  TIMEOUT_1_SECOND,
  TIMEOUT_10_SECONDS,
  TIMEOUT_30_SECONDS,

  } from '../const/constants';


export class SettingsPage {
  readonly page: Page;
  readonly testPlatform: string;
  readonly accountSettingsBtn: Locator;
  readonly connectedAppsBtn: Locator;
  readonly preferencesBtn: Locator;
  readonly themeSelect: Locator;
  readonly languageSelect: Locator;
  readonly defaultTimeZoneSelect: Locator;
  readonly timeFormat12HrBtn: Locator;
  readonly timeFormat24HrBtn: Locator;
  readonly startOfWeekMonBtn: Locator;
  readonly startOfWeekTueBtn: Locator;
  readonly startOfWeekWedBtn: Locator;
  readonly startOfWeekThuBtn: Locator;
  readonly startOfWeekFriBtn: Locator;
  readonly startOfWeekSatBtn: Locator;
  readonly startOfWeekSunBtn: Locator;
  readonly accountSettingsHeader: Locator;
  readonly displayNameInput: Locator;
  readonly bookingPageURLInput: Locator;
  readonly copyLinkBtn: Locator;
  readonly deleteDataBtn: Locator;
  readonly deleteDataConfirmCancelBtn: Locator;
  readonly manageBookingLink: Locator;
  readonly downloadDataBtn: Locator;
  readonly connectedAppsHdr: Locator;
  readonly addCaldavBtn: Locator;
  readonly addCaldavUsernameInput: Locator;
  readonly addCaldavLocationInput: Locator;
  readonly addCaldavPasswordInput: Locator;
  readonly addCaldavCloseModalBtn: Locator;
  readonly addGoogleBtn: Locator;
  readonly defaultCalendarBadge: Locator;
  readonly calendarDropdownTriggers: Locator;
  readonly calendarDropdownSetAsDefault: Locator;
  readonly calendarDropdownDisconnect: Locator;
  readonly calendarCheckboxes: Locator;
  readonly unsavedChangesNotice: Locator;
  readonly saveBtnEN: Locator;
  readonly savedSuccessfullyTextEN: Locator;
  readonly saveBtnDE: Locator;
  readonly revertBtn: Locator;
  readonly googleSignInHdr: Locator;

  constructor(page: Page, testPlatform: string = 'desktop') {
    this.page = page;
    this.testPlatform = testPlatform;

    // main settings view
    this.saveBtnEN = this.page.getByRole('button', { name: 'Save' }).nth(1); // save button at bottom, not in notice bar
    this.savedSuccessfullyTextEN = this.page.getByText('Settings saved successfully', { exact: true });
    this.saveBtnDE = this.page.getByRole('button', { name: 'Speichern' }).nth(1);
    this.revertBtn = this.page.getByRole('button', { name: 'Revert changes' });

    // account settings section
    this.accountSettingsBtn = this.page.getByTestId('settings-accountSettings-settings-btn');
    this.accountSettingsHeader = this.page.getByRole('heading', { name: 'Account Settings' });
    this.displayNameInput = this.page.locator('#booking-page-display-name');
    this.bookingPageURLInput = this.page.locator('#booking-page-url');
    this.copyLinkBtn = this.page.locator('#copy-booking-page-url-button');
    this.deleteDataBtn = this.page.getByRole('button', { name: 'Delete all Appointment data' });
    this.deleteDataConfirmCancelBtn = this.page.getByRole('button', { name: 'Cancel', exact: true });
    this.manageBookingLink = this.page.getByText('Manage booking link');
    this.downloadDataBtn = this.page.getByTestId('settings-account-download-data-btn');

    // preferences section
    this.preferencesBtn = this.page.getByTestId('settings-preferences-settings-btn');
    this.themeSelect = this.page.getByTestId('settings-preferences-theme-select');
    this.languageSelect = this.page.getByTestId('settings-preferences-language-select');
    this.defaultTimeZoneSelect = this.page.getByTestId('settings-preferences-default-time-zone-select');
    this.timeFormat12HrBtn = this.page.getByRole('button', { name: '12:00 AM/PM (12-hour)' });
    this.timeFormat24HrBtn = this.page.getByRole('button', { name: '24:00 (24-hour)' });
    this.startOfWeekMonBtn = this.page.getByRole('button', { name: 'Mon', exact: true });
    this.startOfWeekTueBtn = this.page.getByRole('button', { name: 'Tue', exact: true });
    this.startOfWeekWedBtn = this.page.getByRole('button', { name: 'Wed', exact: true });
    this.startOfWeekThuBtn = this.page.getByRole('button', { name: 'Thu', exact: true });
    this.startOfWeekFriBtn = this.page.getByRole('button', { name: 'Fri', exact: true });
    this.startOfWeekSatBtn = this.page.getByRole('button', { name: 'Sat', exact: true });
    this.startOfWeekSunBtn = this.page.getByRole('button', { name: 'Sun', exact: true });

    // connected apps section
    this.connectedAppsBtn = this.page.getByTestId('settings-connectedApplications-settings-btn');
    this.connectedAppsHdr = this.page.getByRole('heading', { name: 'Connected Applications' });
    this.addCaldavBtn = this.page.getByRole('button', { name: 'Add CalDAV' });
    this.addCaldavUsernameInput = this.page.getByLabel('Username');
    this.addCaldavLocationInput = this.page.getByLabel('Location');
    this.addCaldavPasswordInput = this.page.getByLabel('Password');
    this.addCaldavCloseModalBtn = this.page.getByRole('img', { name: 'Close' });
    this.addGoogleBtn = this.page.getByRole('button', { name: 'Add Google Calendar' });
    this.defaultCalendarBadge = this.page.getByTestId('badge');
    this.calendarDropdownTriggers = this.page.locator('.calendars-container .dropdown');
    this.calendarDropdownSetAsDefault = this.page.getByRole('button', { name: 'Set as default' });
    this.calendarDropdownDisconnect = this.page.locator('.calendars-container .dropdown-inner').getByRole('button', { name: 'Disconnect' });
    this.calendarCheckboxes = this.page.locator('.calendars-container input[type="checkbox"]');
    this.unsavedChangesNotice = this.page.getByText('You have unsaved changes');
    this.googleSignInHdr = this.page.getByText('Sign in with Google');
  }

  /**
   * Scroll the given element into view. The reason why we do this here is because playright doesn't yet supported this on ios.
   */
  async scrollIntoView(targetElement: Locator, timeout: number = 10000) {
    if (!this.testPlatform.includes('ios')) {
      await targetElement.scrollIntoViewIfNeeded({ timeout: timeout });
    }
  }

  /**
   * Navigate to settings, account settings section
   */
  async gotoAccountSettings() {
    await this.page.goto(APPT_SETTINGS_PAGE);
    await this.page.waitForTimeout(TIMEOUT_10_SECONDS);
    // can take some time to populate fields especially in BrowserStack
    if ((await this.displayNameInput.inputValue()).trim() == '') {
      await this.page.waitForTimeout(TIMEOUT_10_SECONDS);
    }
    await this.scrollIntoView(this.accountSettingsBtn);
    await this.accountSettingsBtn.click();
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
  }

  /**
   * Navigate to settings, preferences section
   */
  async gotoPreferencesSettings() {
    await this.page.goto(APPT_SETTINGS_PAGE);
    await this.page.waitForTimeout(TIMEOUT_10_SECONDS);
    await this.scrollIntoView(this.preferencesBtn, TIMEOUT_30_SECONDS);
    await this.preferencesBtn.click();
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
  }

  /**
   * Navigate to settings, connected applications section
   */
  async gotoConnectedAppSettings() {
    await this.page.goto(APPT_SETTINGS_PAGE);
    await this.page.waitForTimeout(TIMEOUT_10_SECONDS);
    await this.scrollIntoView(this.connectedAppsBtn);
    await this.connectedAppsBtn.click();
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
  }
};
