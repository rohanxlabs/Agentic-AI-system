import { siteConfig } from "./site";

export const env = {
  isDevelopment: process.env.NODE_ENV === "development",
  isProduction: process.env.NODE_ENV === "production",
  isServer: typeof window === "undefined",
  ...siteConfig,
};
