import { defineConfig, devices } from "@playwright/test";

if (!process.env.PRIMEAGENT_BASE_PATH_TEST_URL) {
  throw new Error(
    "Set PRIMEAGENT_BASE_PATH_TEST_URL to a prefixed Primeagent deployment.",
  );
}

export default defineConfig({
  testDir: "./tests/live",
  testMatch: "base-path.spec.ts",
  workers: 1,
  retries: 0,
  timeout: 60_000,
  reporter: "list",
  use: {
    ...devices["Desktop Chrome"],
    baseURL: process.env.PRIMEAGENT_BASE_PATH_TEST_URL,
    trace: "retain-on-failure",
  },
});
