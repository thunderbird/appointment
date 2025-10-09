import { type Page, type Locator, expect } from '@playwright/test';

import {
  APPT_SETTINGS_PAGE,
  APPT_HTML_DARK_MODE_CLASS,
  TIMEOUT_1_SECOND,
  TIMEOUT_2_SECONDS,
  TIMEOUT_3_SECONDS,
  TIMEOUT_10_SECONDS,
  TIMEOUT_30_SECONDS,
  APPT_LANGUAGE_SETTING_EN,
  } from '../const/constants';


export class SettingsPage {
  readonly page: Page;
  readonly accountSettingsBtn: Locator;
  readonly connectedAppsBtn: Locator;
  readonly preferencesBtn: Locator;
  readonly themeSelect: Locator;
  readonly languageSelect: Locator;
  readonly settingsHeaderEN: Locator;
  readonly settingsHeaderDE: Locator;
  readonly preferencesHeaderEN: Locator;
  readonly preferencesHeaderDE: Locator;
  readonly defaultTimeZoneSelect: Locator;
  readonly startOfWeekMondayBtn: Locator;
  readonly startOfWeekSundayBtn: Locator;
  readonly accountSettingsHeader: Locator;
  readonly displayNameInput: Locator;
  readonly bookingPageURLInput: Locator;
  readonly copyLinkBtn: Locator;
  readonly cancelServiceBtn: Locator;
  readonly cancelServiceConfirmCancelBtn: Locator;
  readonly bookingPageSettingsBtn: Locator;
  readonly downloadDataBtn: Locator;
  readonly connectedAppsHdr: Locator;
  readonly addCaldavBtn: Locator;
  readonly addCaldavUsernameInput: Locator;
  readonly addCaldavLocationInput: Locator;
  readonly addCaldavPasswordInput: Locator;
  readonly addCaldavCloseModalBtn: Locator;
  readonly addGoogleBtn: Locator;
  readonly defaultCalendarConnectedCbox: Locator;
  readonly saveBtnEN: Locator;
  readonly savedSuccessfullyTextEN: Locator;
  readonly savedSuccessfullyTextDE: Locator;
  readonly saveBtnDE: Locator;
  readonly revertBtn: Locator;


  constructor(page: Page) {
    this.page = page;

    // main settings view
    this.settingsHeaderEN = this.page.getByRole('main').getByText('Settings', { exact: true });
    this.settingsHeaderDE = this.page.getByRole('heading', { name: 'Einstellungen' }).first();
    this.saveBtnEN = this.page.getByRole('button', { name: 'Save' });
    this.savedSuccessfullyTextEN = this.page.getByText('Settings saved successfully', { exact: true });
    this.savedSuccessfullyTextDE = this.page.getByText('Einstellungen erfolgreich gespeichert', { exact: true });
    this.saveBtnDE = this.page.getByRole('button', { name: 'Speichern' });
    this.revertBtn = this.page.getByRole('button', { name: 'Revert changes' });

    // account settings section
    this.accountSettingsBtn = this.page.getByTestId('settings-accountSettings-settings-btn');
    this.accountSettingsHeader = this.page.getByRole('heading', { name: 'Account Settings' });
    this.displayNameInput = this.page.locator('#booking-page-display-name');
    this.bookingPageURLInput = this.page.locator('#booking-page-url');
    this.copyLinkBtn = this.page.locator('#copy-booking-page-url-button');
    this.cancelServiceBtn = this.page.getByRole('button', { name: 'Cancel Service' });
    this.cancelServiceConfirmCancelBtn = this.page.getByRole('button', { name: 'Cancel', exact: true });
    this.bookingPageSettingsBtn = this.page.getByRole('button', { name: 'Booking Page Settings' });
    this.downloadDataBtn = this.page.getByTestId('settings-account-download-data-btn');

    // preferences section
    this.preferencesBtn = this.page.getByTestId('settings-preferences-settings-btn');
    this.themeSelect = this.page.getByTestId('settings-preferences-theme-select');
    this.languageSelect = this.page.getByTestId('settings-preferences-language-select');
    this.preferencesHeaderEN = this.page.getByRole('heading', { name: 'Preferences' })
    this.preferencesHeaderDE = this.page.locator('#preferences').getByRole('heading', { name: 'Einstellungen' });
    this.defaultTimeZoneSelect = this.page.getByTestId('settings-preferences-default-time-zone-select');
    this.startOfWeekMondayBtn = this.page.getByRole('button', { name: 'M', exact: true });
    this.startOfWeekSundayBtn = this.page.getByRole('button', { name: 'S', exact: true });

    // connected apps section
    this.connectedAppsBtn = this.page.getByTestId('settings-connectedApplications-settings-btn');
    this.connectedAppsHdr = this.page.getByRole('heading', { name: 'Connected Applications' });
    this.addCaldavBtn = this.page.getByRole('button', { name: 'Add CalDAV' });
    this.addCaldavUsernameInput = this.page.getByRole('textbox', { name: 'user' });
    this.addCaldavLocationInput = this.page.getByRole('textbox', { name: 'Location The URL or hostname' });
    this.addCaldavPasswordInput = this.page.getByRole('textbox', { name: 'password' });
    this.addCaldavCloseModalBtn = this.page.getByRole('img', { name: 'Close' });
    this.addGoogleBtn = this.page.getByRole('button', { name: 'Add Google Calendar' });
    this.defaultCalendarConnectedCbox = this.page.locator('div').filter({ hasText: /^Default*/ }).getByTestId('checkbox-input');
  }

  /**
   * Navigate to settings, account settings section
   */
  async gotoAccountSettings() {
    await this.page.goto(APPT_SETTINGS_PAGE);
    await this.page.waitForTimeout(TIMEOUT_3_SECONDS);
    await this.accountSettingsBtn.scrollIntoViewIfNeeded();
    await this.accountSettingsBtn.click();
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
  }

  /**
   * Navigate to settings, preferences section
   */
  async gotoPreferencesSettings() {
    await this.page.goto(APPT_SETTINGS_PAGE);
    await this.page.waitForTimeout(TIMEOUT_3_SECONDS);
    await this.preferencesBtn.scrollIntoViewIfNeeded();
    await this.preferencesBtn.click();
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
  }

  /**
   * Navigate to settings, connected applications section
   */
  async gotoConnectedAppSettings() {
    await this.page.goto(APPT_SETTINGS_PAGE);
    await this.page.waitForTimeout(TIMEOUT_3_SECONDS);
    await this.connectedAppsBtn.scrollIntoViewIfNeeded();
    await this.connectedAppsBtn.click();
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
  }

  /**
   * Change the default time zone setting
   */
  async changeDefaultTimezoneSetting(timezone: string) {
    await this.defaultTimeZoneSelect.waitFor( { timeout: TIMEOUT_30_SECONDS });
    await this.defaultTimeZoneSelect.scrollIntoViewIfNeeded();
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    await this.defaultTimeZoneSelect.selectOption(timezone, { timeout: TIMEOUT_30_SECONDS });
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    await this.saveBtnEN.scrollIntoViewIfNeeded();
    await this.saveBtnEN.click();
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    await expect(this.savedSuccessfullyTextEN).toBeVisible();
  }

  /**
   * Change the language setting
   */
  async changeLanguageSetting(currentLanguage: string, newLanguage: string) {
    await this.languageSelect.scrollIntoViewIfNeeded();
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    await this.languageSelect.selectOption(newLanguage, { timeout: TIMEOUT_30_SECONDS });
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    if (currentLanguage == APPT_LANGUAGE_SETTING_EN) {
      await this.saveBtnEN.scrollIntoViewIfNeeded();
      await this.saveBtnEN.click();
      await this.page.waitForTimeout(TIMEOUT_1_SECOND);
      await expect(this.savedSuccessfullyTextDE).toBeVisible();
    } else {
      await this.saveBtnDE.scrollIntoViewIfNeeded();
      await this.saveBtnDE.click();
      await this.page.waitForTimeout(TIMEOUT_1_SECOND);
      await expect(this.savedSuccessfullyTextEN).toBeVisible();
    }
  }

  /**
   * Change the theme setting
   */
  async changeThemeSetting(theme: string) {
    await this.themeSelect.waitFor({ timeout: TIMEOUT_30_SECONDS });
    await this.themeSelect.scrollIntoViewIfNeeded();
    await this.themeSelect.selectOption(theme);
    await this.page.waitForTimeout(TIMEOUT_2_SECONDS);
    await this.saveBtnEN.click();
    await expect(this.savedSuccessfullyTextEN).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    // wait for theme to take affect, can take time especially on browserstack
    await this.page.waitForTimeout(TIMEOUT_10_SECONDS);
  }

  /**
   * Check if dark mode is enabled
   */
  async isDarkModeEnabled(page: Page): Promise<boolean> {
    const htmlTag = page.locator("html");
    const htmlClass = await htmlTag.getAttribute("class");
    return htmlClass === APPT_HTML_DARK_MODE_CLASS;
  }

  /**
   * Change the start of week setting
   */
  async changeStartOfWeekSetting(startOfWeek: string) {
    await this.startOfWeekMondayBtn
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    if (startOfWeek == 'M') {
      await this.startOfWeekMondayBtn.click({ timeout: TIMEOUT_30_SECONDS });
    } else {
      await this.startOfWeekSundayBtn.click({ timeout: TIMEOUT_30_SECONDS });
    }
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    await this.saveBtnEN.scrollIntoViewIfNeeded();
    await this.saveBtnEN.click();
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    await expect(this.savedSuccessfullyTextEN).toBeVisible();
  }

  /**
   * Change the display name setting
   */
  async changeDisplaName(newName: string) {
    await this.displayNameInput.scrollIntoViewIfNeeded();
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    await this.displayNameInput.fill(newName);
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    await this.saveBtnEN.scrollIntoViewIfNeeded();
    await this.saveBtnEN.click();
    await this.page.waitForTimeout(TIMEOUT_3_SECONDS);
  }
}
