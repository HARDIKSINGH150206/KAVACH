import { test, expect } from "@playwright/test";

test("dashboard shell renders", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "KAVACH" })).toBeVisible();
  await expect(page.getByText("Threat level")).toBeVisible();
});

test("demo controls visible", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("Demo Controls")).toBeVisible();
  await expect(page.getByRole("button", { name: /Run demo flow/i })).toBeVisible();
});
