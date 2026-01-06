import { expect, type Page, type Locator } from '@playwright/test';
import { TB_ACCTS_EMAIL, TB_ACCTS_PWORD, TIMEOUT_1_SECOND, TIMEOUT_10_SECONDS, TIMEOUT_30_SECONDS } from '../const/constants';

export class TBAcctsPage {
  readonly page: Page;
  readonly signInHeaderText: Locator;
  readonly userAvatar: Locator;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly signInButton: Locator;
  readonly loginEmailInput: Locator;
  readonly localDevpasswordInput: Locator;
  readonly loginDialogContinueBtn: Locator;

  constructor(page: Page) {
    this.page = page;
    this.signInHeaderText = this.page.getByText('Sign in to your account');
    this.userAvatar = this.page.getByTestId('avatar-default');
    this.emailInput = this.page.getByTestId('username-input');
    this.passwordInput = this.page.getByTestId('password-input');
    this.signInButton = this.page.getByTestId('submit-btn');
    this.loginEmailInput = this.page.getByLabel('Email');
    this.localDevpasswordInput = this.page.getByLabel('Password');
    this.loginDialogContinueBtn = this.page.getByTitle('Continue');
  }

  /**
   * Sign in to TB Accounts using the provided email and password. We provide the playwright
   * test project name (i.e. 'android-chrome') as some actions differ on different mobile platforms.
   */
  async signIn(testProjectName: string = 'desktop') {
    console.log('signing in to TB Accounts');
    expect(TB_ACCTS_EMAIL, 'getting TB_ACCTS_EMAIL env var').toBeTruthy();
    expect(TB_ACCTS_PWORD, 'getting TB_ACCTS_PWORD env var').toBeTruthy();
    await expect(this.emailInput).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await this.emailInput.fill(String(TB_ACCTS_EMAIL));
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    await this.passwordInput.fill(String(TB_ACCTS_PWORD));
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    // 'force' is needed for android but doesn't work on ios
    if (testProjectName.includes('android')) {
      await this.signInButton.click({ force: true });
    } else {
      await this.signInButton.click({ timeout: TIMEOUT_10_SECONDS });
    }
    await this.page.waitForTimeout(TIMEOUT_10_SECONDS);
  }

  /**
   * Sign in when running Appointment on the local dev stack; doesn't redirect to TB Accounts login; just local sign-in
   */
  async localApptSignIn() {
    await expect(this.loginEmailInput).toBeVisible({ timeout: TIMEOUT_30_SECONDS });
    await expect(this.loginDialogContinueBtn).toBeVisible();
    expect(TB_ACCTS_EMAIL, 'getting TB_ACCTS_EMAIL env var').toBeTruthy();
    await this.loginEmailInput.fill(TB_ACCTS_EMAIL);
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    await this.localDevpasswordInput.fill(TB_ACCTS_PWORD);
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    await this.loginDialogContinueBtn.click();
    await this.page.waitForTimeout(TIMEOUT_10_SECONDS);
  }
}
