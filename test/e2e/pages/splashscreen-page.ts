import { expect, type Page, type Locator } from '@playwright/test';
import { APPT_URL, APPT_LOGIN_EMAIL, FXA_PAGE_TITLE, APPT_LOGIN_PWORD, TIMEOUT_30_SECONDS } from '../const/constants';

export class SplashscreenPage {
  readonly page: Page;
  readonly loginBtn: Locator;
  readonly signUpBetaBtn: Locator;
  readonly loginEmailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginContinueBtn: Locator;

  constructor(page: Page) {
    this.page = page;
    this.loginBtn = this.page.getByTestId('home-login-btn');
    this.signUpBetaBtn = this.page.getByTestId('home-sign-up-beta-btn');
    this.loginEmailInput = this.page.getByLabel('Email address');
    this.passwordInput = this.page.getByLabel('Password');
    this.loginContinueBtn = this.page.getByTitle('Continue');
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
    await this.loginContinueBtn.click();
  }

  async getToFxA() {
    await expect(this.loginBtn).toBeVisible();
    await this.clickLoginBtn();
    await expect(this.loginEmailInput).toBeVisible();
    await expect(this.loginContinueBtn).toBeVisible();
    expect(APPT_LOGIN_EMAIL, 'getting APPT_LOGIN_EMAIL env var').toBeTruthy();
    await this.enterLoginEmail(APPT_LOGIN_EMAIL);
    await this.clickLoginContinueBtn();
    await expect(this.page).toHaveTitle(FXA_PAGE_TITLE, { timeout: TIMEOUT_30_SECONDS }); // be generous in case FxA is slow to load
  }

  async localApptSignIn() {
    await expect(this.loginBtn).toBeVisible();
    await this.clickLoginBtn();
    await expect(this.loginEmailInput).toBeVisible();
    await expect(this.loginContinueBtn).toBeVisible();
    expect(APPT_LOGIN_EMAIL, 'getting APPT_LOGIN_EMAIL env var').toBeTruthy();
    await this.enterLoginEmail(APPT_LOGIN_EMAIL);
    await this.enterPassword(APPT_LOGIN_PWORD);
    await this.clickLoginContinueBtn();
  }
}
