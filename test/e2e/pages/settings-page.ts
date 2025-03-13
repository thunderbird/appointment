import { expect, type Page, type Locator } from '@playwright/test';

import {
  APPT_MAIN_SETTINGS_PAGE,
  APPT_GENERAL_SETTINGS_PAGE,
  APPT_ACCOUNT_SETTINGS_PAGE,
  APPT_CALENDAR_SETTINGS_PAGE,
  APPT_CONNECTED_SETTINGS_PAGE,
  APPT_HTML_DARK_MODE_CLASS,
} from '../const/constants';
import { waitForDebugger } from 'inspector';
import { domainToASCII } from 'url';

export class SettingsPage {
  readonly page: Page;
  readonly settingsHeaderEN: Locator;
  readonly settingsHeaderDE: Locator;
  readonly generalSettingsBtn: Locator;
  readonly calendarSettingsBtn: Locator;
  readonly accountSettingsBtn: Locator;
  readonly connectedSettingsBtn: Locator;
  readonly generalSettingsHeaderEN: Locator;
  readonly generalSettingsHeaderDE: Locator;
  readonly calendarSettingsHeader: Locator;
  readonly accountSettingsHeader: Locator;
  readonly connectedSettingsHeader: Locator;
  readonly languageSelect: Locator;
  readonly themeSelect: Locator;
  readonly htmlAttribLocator: Locator;
  readonly settings12hrRadio: Locator;
  readonly settings24hrRadio: Locator;
  readonly timeZoneSelect: Locator;
  readonly profileUsernameInput: Locator;
  readonly profilePreferredEmailSelect: Locator;
  readonly profileDisplayNameInput: Locator;
  readonly profileMyLinkInput: Locator;
  readonly profileSaveChangesBtn: Locator;
  readonly refreshLinkBtn: Locator;
  readonly confirmRefreshCancelBtn: Locator;
  readonly inviteCodesHeader: Locator;
  readonly noInviteCodesCell: Locator;

  constructor(page: Page) {
    this.page = page;
    this.settingsHeaderEN = this.page.getByRole('main').getByText('Settings', { exact: true });
    this.settingsHeaderDE = this.page.getByRole('main').getByText('Einstellungen', { exact: true });
    this.generalSettingsBtn = this.page.getByTestId('settings-general-settings-btn');
    this.calendarSettingsBtn = this.page.getByTestId('settings-calendar-settings-btn');
    this.accountSettingsBtn = this.page.getByTestId('settings-account-settings-btn');
    this.connectedSettingsBtn = this.page.getByTestId('settings-connectedAccounts-settings-btn');
    this.generalSettingsHeaderEN = this.page.getByText('General Settings', { exact: true });
    this.generalSettingsHeaderDE = this.page.getByText('Allgemeine Einstellungen', { exact: true });
    this.calendarSettingsHeader = this.page.getByText('Calendar Settings', { exact: true });
    this.accountSettingsHeader = this.page.getByText('Account Settings', { exact: true });
    this.connectedSettingsHeader = this.page.getByText('Connected Accounts Settings', { exact: true });
    this.languageSelect = this.page.getByTestId('settings-general-locale-select');
    this.themeSelect = this.page.getByTestId('settings-general-theme-select');
    this.htmlAttribLocator = this.page.locator("html");
    this.settings12hrRadio = this.page.getByText('12-hour AM/PM', { exact: true });
    this.settings24hrRadio = this.page.getByText('24-hour', { exact: true });
    this.timeZoneSelect = this.page.getByTestId('settings-general-timezone-select');
    this.profileUsernameInput = this.page.getByTestId('settings-account-user-name-input');
    this.profilePreferredEmailSelect = this.page.getByTestId('settings-account-email-select');
    this.profileDisplayNameInput = this.page.getByTestId('settings-account-display-name-input');
    this.profileMyLinkInput = this.page.getByTestId('settings-account-mylink-input');
    this.profileSaveChangesBtn = this.page.getByTestId('settings-account-save-changes-btn');
    this.refreshLinkBtn = this.page.getByTestId('settings-account-refresh-link-btn');
    this.confirmRefreshCancelBtn = this.page.getByRole('button', { name: 'Cancel' });
    this.noInviteCodesCell = this.page.getByRole('cell', { name: 'No Invite Codes could be' });
    this.inviteCodesHeader = this.page.getByText('Invites', { exact: true });
  }

  /**
   * Navigate directly to the main settings page
   */
  async gotoMainSettingsPage() {
    await this.page.goto(APPT_MAIN_SETTINGS_PAGE, { waitUntil: 'domcontentloaded' });
  }

  /**
   * Navigate directly to the general settings page
   */
  async gotoGeneralSettingsPage() {
    await this.page.goto(APPT_GENERAL_SETTINGS_PAGE, { waitUntil: 'domcontentloaded' });
  }

  /**
   * Navigate directly to the calendar settings page
   */
  async gotoCalendarSettingsPage() {
    await this.page.goto(APPT_CALENDAR_SETTINGS_PAGE, { waitUntil: 'domcontentloaded' });
  }

  /**
   * Navigate directly to the account settings page
   */
  async gotoAccountSettingsPage() {
    await this.page.goto(APPT_ACCOUNT_SETTINGS_PAGE, { waitUntil: 'domcontentloaded' });
  }

  /**
   * Navigate directly to the connected accounts settings page
   */
  async gotoConnectedAccountsSettingsPage() {
    await this.page.goto(APPT_CONNECTED_SETTINGS_PAGE, { waitUntil: 'domcontentloaded' });
  }

  /**
   * Change the general setting's page language setting
   */
  async changeLanguageSetting(language: string) {
    await this.languageSelect.selectOption(language, { timeout: 30000 });
  }

  /**
   * Change the general setting's page theme setting
   */
  async changeThemeSetting(theme: string) {
    await this.themeSelect.selectOption(theme, { timeout: 30000 });
  }

  /**
   * Check if dark mode is enabled
   */
  async isDarkModeEnabled(page: Page): Promise<boolean> {
    const htmlTag = page.locator("html");
    const htmlClass = await htmlTag.getAttribute("class");

    if (htmlClass == APPT_HTML_DARK_MODE_CLASS) {
      return true;
    } else {
      return false;
    }
  }

  /**
   * Change time format settings to 12-hour format
   */
  async set12hrFormat() {
    // give a few seconds to be applied as sometimes the test runs so fast
    // it switches back to the dashboard tab before the time format is applied
    await this.settings12hrRadio.click( { timeout: 30000 });
    await this.page.waitForTimeout(3000); // give a few seconds to be applied
  }

  /**
   * Change time format settings to 24-hour format
   */
  async set24hrFormat() {
    await this.settings24hrRadio.click({ timeout: 30000 });
    // give a few seconds to be applied as sometimes the test runs so fast
    // it switches back to the dashboard tab before the time format is applied
    await this.page.waitForTimeout(3000);
  }

  /**
   * Change the general setting's time zone setting
   */
  async changeTimezoneSetting(timezone: string) {
    await this.timeZoneSelect.selectOption(timezone, { timeout: 30000 });
    await this.page.waitForTimeout(3000); // give a few seconds to be applied
  }

  /**
   * Get the account settings profile username value
   */
  async getAccountProfileUsername(): Promise<string> {
    return await this.profileUsernameInput.inputValue();
  }

  /**
   * Get the account settings profile preferred email value
   */
  async getAccountProfilePreferredEmail(): Promise<string> {
    return await this.profilePreferredEmailSelect.inputValue();
  }

  /**
   * Get the account settings profile display name value
   */
  async getAccountProfileDisplayName(): Promise<string> {
    return await this.profileDisplayNameInput.inputValue();
  }

  /**
   * Set the account settings profile display name value
   */
  async setAccountProfileDisplayName(newDisplayName: string) {
    await this.profileDisplayNameInput.fill(newDisplayName);
    await this.profileSaveChangesBtn.click();
    await this.page.waitForTimeout(3000); // give a few seconds to be applied
  }

  /**
   * Get the account settings profile my link value
   */
  async getAccountProfileMyLink(): Promise<string> {
    return await this.profileMyLinkInput.inputValue();
  }
}
