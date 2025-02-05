import { expect, type Page, type Locator } from '@playwright/test';
import { APPT_URL, PROD_LOGIN_EMAIL, FXA_PAGE_TITLE } from '../const/constants';

export class SplashscreenPage {
  readonly page: Page;
  readonly loginBtn: Locator;
  readonly signUpBetaBtn: Locator;
  readonly loginEmailInput: Locator;
  readonly loginContinueBtn: Locator;

  constructor(page: Page) {
    this.page = page;
    this.loginBtn = this.page.getByTestId('home-login-btn');
    this.signUpBetaBtn = this.page.getByTestId('home-sign-up-beta-btn');
    this.loginEmailInput = this.page.getByLabel('Email address');
    this.loginContinueBtn = this.page.getByTitle('Continue');
  }

  async gotoProd() {
    await this.page.goto(APPT_URL);
    await this.page.waitForLoadState('domcontentloaded');
  }

  async clickLoginBtn() {
    await this.loginBtn.click();
  }

  async enterLoginEmail(emailAddress: string) {
    await this.loginEmailInput.fill(emailAddress);
  }

  async clickLoginContinueBtn() {
    await this.loginContinueBtn.click();
  }

  async getToFxA() {
    await expect(this.loginBtn).toBeVisible();
    await this.clickLoginBtn();
    await expect(this.loginEmailInput).toBeVisible();
    await expect(this.loginContinueBtn).toBeVisible();
    expect(PROD_LOGIN_EMAIL, 'getting APPT_LOGIN_EMAIL env var').toBeTruthy();
    await this.enterLoginEmail(String(PROD_LOGIN_EMAIL))
    await this.clickLoginContinueBtn();
    await expect(this.page).toHaveTitle(FXA_PAGE_TITLE, { timeout: 30_000 }); // be generous in case FxA is slow to load
  }
}
