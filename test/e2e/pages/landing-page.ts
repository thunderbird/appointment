import { expect, type Page, type Locator } from '@playwright/test';
import {
  APPT_URL,
  TB_ACCTS_PAGE_TITLE,
  TB_ACCTS_EMAIL,
  TB_ACCTS_PWORD,
  TIMEOUT_30_SECONDS,
  TIMEOUT_90_SECONDS,
  TIMEOUT_60_SECONDS,
 } from '../const/constants';

export class LandingPage {
  readonly page: Page;
  readonly hamburgerMenu: Locator;
  readonly signinBtn: Locator;
  readonly homeContinueBtn: Locator;
  readonly loginEmailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginDialogContinueBtn: Locator;

  constructor(page: Page) {
    this.page = page;
    this.hamburgerMenu = this.page.locator('#mobile-hamburger-button');
    this.signinBtn = this.page.getByRole('button', { name: 'Sign in' });
    this.homeContinueBtn = this.page.getByTestId('home-continue-btn');
    this.loginEmailInput = this.page.getByLabel('Email address');
    this.passwordInput = this.page.getByLabel('Password');
    this.loginDialogContinueBtn = this.page.getByTitle('Continue');
  }

  async gotoLandingPage() {
    await this.page.goto(APPT_URL, { timeout: TIMEOUT_60_SECONDS });
  }

  async clicksigninBtn() {
    await this.signinBtn.click();
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
   * From the first Appointment landing page, get us to the TB Accounts/TB Pro sign-in page.
   */
  async getToTBAccts(mobile: boolean) {
    // on the landing/marketing page we just need to choose to sign in, that will redirect us to TB Accounts
    // on desktop there is a 'sign in' button visible, on mobile we need to click hamburger menu first
    if (mobile) {
      await expect(this.hamburgerMenu).toBeVisible( { timeout: TIMEOUT_30_SECONDS });
      await this.hamburgerMenu.click();
    }

    await expect(this.signinBtn).toBeVisible( { timeout: TIMEOUT_30_SECONDS });
    await this.signinBtn.scrollIntoViewIfNeeded();
    await this.signinBtn.click();
    
    // be generous in case TB Accounts sign-in is slow to load
    await expect(this.page).toHaveTitle(new RegExp(`^${TB_ACCTS_PAGE_TITLE}`), { timeout: TIMEOUT_90_SECONDS });
  }

  /**
   * Sign in when running Appointment on the local dev stack; doesn't redirect to TB Accounts login; just local sign-in
   */
  async localApptSignIn() {
    await expect(this.loginEmailInput).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await expect(this.loginDialogContinueBtn).toBeVisible();
    expect(TB_ACCTS_EMAIL, 'getting TB_ACCTS_EMAIL env var').toBeTruthy();
    await this.enterUsername(TB_ACCTS_EMAIL);
    await this.enterPassword(TB_ACCTS_PWORD);
    await this.clickLoginContinueBtn();
  }
}
