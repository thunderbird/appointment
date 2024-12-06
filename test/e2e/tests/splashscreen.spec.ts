import { test, expect } from '@playwright/test';
import { APPT_PROD_URL, APPT_PAGE_TITLE } from '../const/constants';

// verify main appointment splash screen appears
test.describe('splash screen', {
  tag: '@prod-sanity'
}, () => {
  test('has title', async ({ page }) => {
    await page.goto(APPT_PROD_URL);
    await expect(page).toHaveTitle(APPT_PAGE_TITLE);
  });

  // todo: more checks on splash screen appearance
});
