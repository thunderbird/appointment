import { expect, type Page, type Locator } from '@playwright/test';
import { PROD_LOGIN_PWORD } from '../const/constants';

export class FxAPage {
  readonly page: Page;
  readonly signInHeaderText: Locator;
  readonly userAvatar: Locator;
  readonly passwordInput: Locator;
  readonly signInButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.signInHeaderText = this.page.getByText('Enter your password');
    this.userAvatar = this.page.getByTestId('avatar-default');
    this.passwordInput = this.page.getByRole('textbox', {name: 'password' });
    this.signInButton = this.page.getByRole('button', { name: 'Sign in' });
  }

  async signIn() {
    expect(PROD_LOGIN_PWORD, 'getting APPT_LOGIN_PWORD env var').toBeTruthy();
    await this.passwordInput.fill(String(PROD_LOGIN_PWORD));
    await this.signInButton.click();
  }
}
