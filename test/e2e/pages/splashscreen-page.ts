import { expect, type Page, type Locator } from '@playwright/test';
import { APPT_PROD_URL, PROD_LOGIN_EMAIL, FXA_PAGE_TITLE } from '../const/constants';

export class SplashscreenPage {
  readonly page: Page;
  readonly loginBtn: Locator;
  readonly signUpBetaBtn: Locator;
  readonly loginEmailInput: Locator;
  readonly loginContinueBtn: Locator;

  constructor(page: Page) {
    this.page = page;
    //update this after data-testid 's are deployed to prod
    //this.loginBtn = this.page.getByTestId('home-login-btn');
    this.loginBtn = this.page.getByTitle('Log in');
    //update this after data-testid 's are deployed to prod
    //this.signUpBetaBtn = this.page.getByTestId('home-sign-up-beta-btn');
    this.signUpBetaBtn = this.page.getByTitle('Sign up for the beta');
    //update this after data-testid 's are deployed to prod
    //this.loginEmailInput = this.page.getByTestId('login-email-input');
    this.loginEmailInput = this.page.getByLabel('Email address');
    //update this after data-testid 's are deployed to prod    
    //this.loginContinueBtn = this.page.getByTestId('login-continue-btn');
    this.loginContinueBtn = this.page.getByTitle('Continue');
  }

  async gotoProd() {
    await this.page.goto(APPT_PROD_URL);
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
    expect(PROD_LOGIN_EMAIL, 'getting APPT_PROD_LOGIN_EMAIL env var').toBeTruthy();
    await this.enterLoginEmail(String(PROD_LOGIN_EMAIL))
    await this.clickLoginContinueBtn();
    await expect(this.page).toHaveTitle(FXA_PAGE_TITLE, { timeout: 30_000 }); // be generous in case FxA is slow to load
  }
}
