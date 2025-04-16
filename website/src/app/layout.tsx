import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: '--font-inter',
  display: 'swap',
});

const playfair = Playfair_Display({
  subsets: ["latin"],
  variable: '--font-playfair',
  display: 'swap',
});

export const metadata: Metadata = {
  title: "EGOS Project",
  description: "Quantum Unified Master System - Exploring Ethical AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${playfair.variable}`}>
      <body className="flex flex-col min-h-screen">
        <header className="bg-egos-blue text-white p-4 shadow-md">
          Header Placeholder
        </header>
        <main className="flex-grow container mx-auto p-4 md:p-6 lg:p-8">
          {children}
        </main>
        <footer className="bg-neutral-200 text-neutral-700 text-center p-4 mt-auto">
          Footer Placeholder 2025 EGOS
        </footer>
      </body>
    </html>
  );
}
