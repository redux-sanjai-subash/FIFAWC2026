import type { Metadata, Viewport } from "next";
import "./globals.css";
import { AuthProvider } from "@/components/AuthProvider";
import { ThemeProvider, themeInitScript } from "@/components/ThemeProvider";
import { ToastProvider } from "@/components/ToastProvider";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "Prediction Club",
  description: "A premium prediction club.",
};

export const viewport: Viewport = {
  themeColor: "#09090C",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-theme="dark" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
      </head>
      <body>
        <ThemeProvider>
          <ToastProvider>
            <AuthProvider>
              <Navbar />
              <main className="container-lux py-10 sm:py-16">{children}</main>
              <footer className="container-lux flex flex-col items-center gap-2 border-t border-fg/10 py-10 text-center">
              </footer>
            </AuthProvider>
          </ToastProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
