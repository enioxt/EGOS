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

// Import layout components
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';

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
      <body className="flex flex-col min-h-screen bg-egos-light-gray text-neutral-900 antialiased">
        {/* Apply base text/bg here instead of globals.css body */} 
        <Header /> {/* Use Header component */}
        <main className="flex-grow container mx-auto p-4 md:p-6 lg:p-8">
          {children}
        </main>
        <Footer /> {/* Use Footer component */}
      </body>
    </html>
  );
}
