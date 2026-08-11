import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Providers } from "@/providers/tanstack-query";
import { ThemeProvider } from "@/providers/theme-provider";
import { ToastProvider } from "@/providers/toast-provider";
import { siteConfig } from "@/config/site";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: siteConfig.name,
    template: `%s | ${siteConfig.name}`,
  },
  description: siteConfig.description,
  metadataBase: new URL(siteConfig.url),
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-background text-foreground">
        <Providers>
          <ThemeProvider>
            <ToastProvider>
              <div className="flex-1 flex flex-col">
                <header className="border-b border-border bg-card">
                  <div className="container mx-auto px-4 py-4">
                    <h1 className="text-2xl font-bold">Agentic AI System</h1>
                    <p className="text-sm text-muted-foreground">Autonomous Multi-Agent System</p>
                  </div>
                </header>
                <main className="flex-1 container mx-auto">
                  {children}
                </main>
              </div>
            </ToastProvider>
          </ThemeProvider>
        </Providers>
      </body>
    </html>
  );
}
