import { expect, type Page, type Locator } from '@playwright/test';
import {
  APPT_URL,
  APPT_USERNAME,
  TB_ACCTS_PAGE_TITLE,
  TB_ACCTS_PWORD,
  TIMEOUT_1_SECOND,
  TIMEOUT_30_SECONDS,
  TIMEOUT_90_SECONDS,
  TIMEOUT_60_SECONDS,
 } from '../const/constants';

export class LoginPage {
  readonly page: Page;
  readonly loginBtn: Locator;
  readonly homeContinueBtn: Locator;
  readonly signUpBetaBtn: Locator;
  readonly loginEmailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginDialogContinueBtn: Locator;

  constructor(page: Page) {
    this.page = page;
    this.loginBtn = this.page.getByTestId('home-login-btn');
    this.homeContinueBtn = this.page.getByTestId('home-continue-btn');
    this.signUpBetaBtn = this.page.getByTestId('home-sign-up-beta-btn');
    this.loginEmailInput = this.page.getByLabel('Email address');
    this.passwordInput = this.page.getByLabel('Password');
    this.loginDialogContinueBtn = this.page.getByTitle('Continue');
  }

  async gotoDashboard() {
    await this.page.goto(APPT_URL, { timeout: TIMEOUT_60_SECONDS });
  }

  async clickLoginBtn() {
    await this.loginBtn.click();
  }

  async enterUsername(emailAddress: string) {
    await this.loginEmailInput.fill(emailAddress);
  }

  async enterPassword(password: string) {
    await this.passwordInput.fill(password);
  }

  async clickLoginContinueBtn() {
    await this.loginDialogContinueBtn.click();
  }


  /**
   * Sign in on the main Appointment login page, which will redirect us to sign in with TB Accounts. 
   */
  async getToTBAccts() {
    await expect(this.loginBtn).toBeVisible( { timeout: TIMEOUT_30_SECONDS });
    await this.clickLoginBtn();
    await expect(this.loginEmailInput).toBeVisible( { timeout: TIMEOUT_30_SECONDS });
    await expect(this.loginDialogContinueBtn).toBeVisible();
    expect(APPT_USERNAME, 'getting APPT_USERNAME env var').toBeTruthy();
    await this.enterUsername(APPT_USERNAME);
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    await this.clickLoginContinueBtn();
    // be generous in case TB Accounts sign-in is slow to load
    await expect(this.page).toHaveTitle(new RegExp(`^${TB_ACCTS_PAGE_TITLE}`), { timeout: TIMEOUT_90_SECONDS });
  }

  /**
   * Sign in when running Appointment on the local dev stack, doesn't require TB Accounts login.
   */
  async localApptSignIn() {
    await expect(this.loginBtn).toBeVisible();
    await this.clickLoginBtn();
    await expect(this.loginEmailInput).toBeVisible();
    await expect(this.loginDialogContinueBtn).toBeVisible();
    expect(APPT_USERNAME, 'getting APPT_USERNAME env var').toBeTruthy();
    await this.enterUsername(APPT_USERNAME);
    await this.enterPassword(TB_ACCTS_PWORD);
    await this.clickLoginContinueBtn();
  }
}
