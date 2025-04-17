// Simplified layout for debugging
import { Inter, EB_Garamond } from "next/font/google";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import React from 'react'; // Ensure React is imported

const inter = Inter({ subsets: ["latin"], variable: '--font-inter' });
const garamond = EB_Garamond({
  subsets: ['latin'],
  weight: ['400', '700'], // Include weights used
  variable: '--font-garamond'
});

// Simplified Props - Still need locale but NOT as a Promise for sync component
interface RootLayoutProps {
  children: React.ReactNode;
  params: { locale: string }; // Reverted params type for basic sync layout
}

// Simplified synchronous RootLayout
export default function RootLayout({ children, params }: RootLayoutProps) {
  const { locale } = params; // Direct access, no await

  return (
    <html lang={locale} className={`${inter.variable} ${garamond.variable}`}>
      <body className="bg-background text-text font-sans">
        {/* Removed NextIntlClientProvider and useMessages */}
        <Header />
        <main className="pt-16"> {/* Adjust padding-top based on fixed header height */}
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}