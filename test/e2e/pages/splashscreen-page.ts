import { expect, type Page, type Locator } from '@playwright/test';
import {
  APPT_URL,
  APPT_LOGIN_EMAIL,
  APPT_DISPLAY_NAME,
  FXA_PAGE_TITLE,
  APPT_LOGIN_PWORD, 
  TIMEOUT_1_SECOND,
  TIMEOUT_3_SECONDS,
  TIMEOUT_30_SECONDS,
  TIMEOUT_90_SECONDS,
  APPT_TIMEZONE_SETTING_PRIMARY,
 } from '../const/constants';

export class SplashscreenPage {
  readonly page: Page;
  readonly loginBtn: Locator;
  readonly homeContinueBtn: Locator;
  readonly signUpBetaBtn: Locator;
  readonly loginEmailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginDialogContinueBtn: Locator;
  readonly createProfileHeader: Locator;
  readonly createProfileFullNameInput: Locator;
  readonly createProfileUsernameInput: Locator;
  readonly createProfileTimezoneSelect: Locator;
  readonly connectGoogleCalBtn: Locator;
  readonly signInGoogleHdr: Locator;
  readonly signInGoogleNextBtn: Locator;

  constructor(page: Page) {
    this.page = page;
    this.loginBtn = this.page.getByTestId('home-login-btn');
    this.homeContinueBtn = this.page.getByTestId('home-continue-btn');
    this.signUpBetaBtn = this.page.getByTestId('home-sign-up-beta-btn');
    this.loginEmailInput = this.page.getByLabel('Email address');
    this.passwordInput = this.page.getByLabel('Password');
    this.loginDialogContinueBtn = this.page.getByTitle('Continue');
    this.createProfileHeader = this.page.getByText('Create your profile');
    this.createProfileFullNameInput = this.page.getByLabel('Full Name');
    this.createProfileUsernameInput = this.page.getByLabel('Username');
    this.createProfileTimezoneSelect = this.page.getByLabel('Time Zone');
    this.connectGoogleCalBtn = this.page.getByTitle('Connect Google Calendar');
    this.signInGoogleHdr = this.page.getByText('Sign in with Google');
    this.signInGoogleNextBtn = this.page.getByRole('button', { name: 'Next' });
  }

  async gotoDashboard() {
    await this.page.goto(APPT_URL);
  }

  async clickLoginBtn() {
    await this.loginBtn.click();
  }

  async enterLoginEmail(emailAddress: string) {
    await this.loginEmailInput.fill(emailAddress);
  }

  async enterPassword(password: string) {
    await this.passwordInput.fill(password);
  }

  async clickLoginContinueBtn() {
    await this.loginDialogContinueBtn.click();
  }

  async getToFxA() {
    await expect(this.loginBtn).toBeVisible( { timeout: TIMEOUT_30_SECONDS });
    await this.clickLoginBtn();
    await expect(this.loginEmailInput).toBeVisible( { timeout: TIMEOUT_30_SECONDS });
    await expect(this.loginDialogContinueBtn).toBeVisible();
    expect(APPT_LOGIN_EMAIL, 'getting APPT_LOGIN_EMAIL env var').toBeTruthy();
    await this.enterLoginEmail(APPT_LOGIN_EMAIL);
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    await this.clickLoginContinueBtn();
    await expect(this.page).toHaveTitle(FXA_PAGE_TITLE, { timeout: TIMEOUT_90_SECONDS }); // be generous in case FxA is slow to load
  }

  async localApptSignIn() {
    await expect(this.loginBtn).toBeVisible();
    await this.clickLoginBtn();
    await this.page.waitForTimeout(TIMEOUT_3_SECONDS);
    await expect(this.loginEmailInput).toBeVisible();
    await expect(this.loginDialogContinueBtn).toBeVisible();
    expect(APPT_LOGIN_EMAIL, 'getting APPT_LOGIN_EMAIL env var').toBeTruthy();
    await this.enterLoginEmail(APPT_LOGIN_EMAIL);
    await this.enterPassword(APPT_LOGIN_PWORD);
    await this.clickLoginContinueBtn();
    await this.page.waitForTimeout(TIMEOUT_3_SECONDS);
  }

  async firstTimeUserSetup() {
    // first time appt is running for this user, so go through the ftue (starting at the create profile page)
    console.log('going through FTUE')
    await expect(this.createProfileFullNameInput).toHaveValue(APPT_DISPLAY_NAME);
    await expect(this.createProfileUsernameInput).toHaveValue(APPT_LOGIN_EMAIL);

    // select timezone
    await this.changeTimezone(APPT_TIMEZONE_SETTING_PRIMARY)

    // continue to next screen
    await this.loginDialogContinueBtn.click();
    await this.page.waitForTimeout(TIMEOUT_3_SECONDS);

    // now select calendar provider
    await this.connectGoogleCalBtn.click();
    await this.page.waitForTimeout(TIMEOUT_3_SECONDS);

    // now on sign-in with google page
    await expect(this.signInGoogleHdr).toBeVisible();
    await this.signInGoogleNextBtn.click();
    await this.page.waitForTimeout(TIMEOUT_3_SECONDS);

    // google 'couldn't sign you in' error, says browser not secure
  }

  async changeTimezone(timezone: string) {
    await this.createProfileTimezoneSelect.scrollIntoViewIfNeeded();
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    await this.createProfileTimezoneSelect.selectOption(timezone, { timeout: TIMEOUT_30_SECONDS });
    await this.page.waitForTimeout(TIMEOUT_1_SECOND); // give a few seconds to be applied
  }
}
