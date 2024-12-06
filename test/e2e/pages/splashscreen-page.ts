import { type Page, type Locator } from '@playwright/test';
import { APPT_PROD_URL } from '../const/constants';

export class SplashscreenPage {
  readonly page: Page;
  readonly loginBtn: Locator;
  readonly signUpBetaBtn: Locator;

  constructor(page: Page) {
    this.page = page;
    this.loginBtn = this.page.getByTestId('home-login-btn');
    this.signUpBetaBtn = this.page.getByTestId('home-sign-up-beta-btn');
  }

  async gotoProd() {
    await this.page.goto(APPT_PROD_URL);
  }
}
