import type { Metadata } from "next";
import { Inter, EB_Garamond } from "next/font/google";
import "./globals.css"; // Path updated
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";

// Import Font Awesome CSS
import '@fortawesome/fontawesome-svg-core/styles.css';
import { config } from '@fortawesome/fontawesome-svg-core';
config.autoAddCss = false; // Prevent Font Awesome from adding its own CSS

// Import next-intl
import { NextIntlClientProvider, useMessages } from 'next-intl';

const inter = Inter({ subsets: ["latin"], variable: '--font-inter' });
const garamond = EB_Garamond({ 
  subsets: ['latin'],
  weight: ['400', '700'], // Include weights used
  variable: '--font-garamond'
});

export const metadata: Metadata = {
  title: "EGOS Project",
  description: "Evolving Generative Operating System - An open-source framework for conscious AI development.",
};

// Define props type to include locale
interface RootLayoutProps {
  children: React.ReactNode;
  params: {
    locale: string;
  };
}

export default function RootLayout({ children, params: { locale } }: Readonly<RootLayoutProps>) {
  // Receive messages provided in `i18n.ts`
  const messages = useMessages();

  return (
    <html lang={locale} className={`${inter.variable} ${garamond.variable}`}> 
      <body className="bg-background text-text font-sans">
        <NextIntlClientProvider locale={locale} messages={messages}>
          <Header />
          <main className="pt-16"> {/* Adjust padding-top based on fixed header height */}
            {children}
          </main>
          <Footer />
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
