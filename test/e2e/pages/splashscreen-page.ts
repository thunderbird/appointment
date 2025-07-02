import { expect, type Page, type Locator } from '@playwright/test';
import {
  APPT_URL,
  APPT_LOGIN_EMAIL,
  FXA_PAGE_TITLE,
  APPT_LOGIN_PWORD, 
  TIMEOUT_1_SECOND,
  TIMEOUT_30_SECONDS,
  TIMEOUT_90_SECONDS,
  TIMEOUT_60_SECONDS,
 } from '../const/constants';

export class SplashscreenPage {
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
    await expect(this.loginEmailInput).toBeVisible();
    await expect(this.loginDialogContinueBtn).toBeVisible();
    expect(APPT_LOGIN_EMAIL, 'getting APPT_LOGIN_EMAIL env var').toBeTruthy();
    await this.enterLoginEmail(APPT_LOGIN_EMAIL);
    await this.enterPassword(APPT_LOGIN_PWORD);
    await this.clickLoginContinueBtn();
  }
}
