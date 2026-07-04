/**
 * @next/next/google-fonts compatibility
 * We import fonts directly in layout.tsx for better control.
 */
export const siteConfig = {
  name: "Agentic AI System",
  description: "Intelligent autonomous agent platform",
  url: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  apiUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  apiKey: process.env.NEXT_PUBLIC_API_KEY || "",
} as const;

export type SiteConfig = typeof siteConfig;
