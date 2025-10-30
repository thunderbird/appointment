import { expect, type Page, type Locator } from '@playwright/test';
import { TB_ACCTS_EMAIL, TB_ACCTS_PWORD, TIMEOUT_10_SECONDS, TIMEOUT_1_SECOND } from '../const/constants';

export class TBAcctsPage {
  readonly page: Page;
  readonly signInHeaderText: Locator;
  readonly userAvatar: Locator;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly signInButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.signInHeaderText = this.page.getByText('Enter your password');
    this.userAvatar = this.page.getByTestId('avatar-default');
    this.emailInput = this.page.getByTestId('username-input');
    this.passwordInput = this.page.getByTestId('password-input');
    this.signInButton = this.page.getByRole('button', { name: 'Sign in' });
  }

  /**
   * Sign in to TB Accounts using the provided email and password.
   */
  async signIn() {
    console.log('signing in to TB Accounts');
    expect(TB_ACCTS_EMAIL, 'getting TB_ACCTS_EMAIL env var').toBeTruthy();
    expect(TB_ACCTS_PWORD, 'getting TB_ACCTS_PWORD env var').toBeTruthy();
    await this.emailInput.fill(String(TB_ACCTS_EMAIL));
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    await this.passwordInput.fill(String(TB_ACCTS_PWORD));
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    await this.page.waitForTimeout(TIMEOUT_1_SECOND);
    await this.signInButton.click({ force: true });
    await this.page.waitForTimeout(TIMEOUT_10_SECONDS);
  }
}
