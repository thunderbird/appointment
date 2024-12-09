import { expect, type Page, type Locator } from '@playwright/test';

export class DashboardPage {
  readonly page: Page;
  readonly navBarDashboardBtn: Locator;
  readonly userMenuAvatar: Locator;

  constructor(page: Page) {
    this.page = page;
    // temporary; update after next deployment when my test-dataid's are deployed
    //this.navBarDashboardBtn = this.page.getByTestId('nav-bar-dashboard-button');
    this.navBarDashboardBtn = this.page.getByRole('link', { name: 'Dashboard' });
    // temporary; update after next deployment when my test-dataid's are deployed
    //this.userMenuAvatar = this.page.getByTestId('user-menu-avatar');
    this.userMenuAvatar = this.page.locator('.flex-center');
  }
}
