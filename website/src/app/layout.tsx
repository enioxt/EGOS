import type { Metadata } from "next";
import { Inter, EB_Garamond } from "next/font/google";
import "./globals.css";

// Import Components
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";

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

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: Readonly<RootLayoutProps>) {
  return (
    <html lang="en" className={`${inter.variable} ${garamond.variable}`}> 
      <body className="bg-background text-foreground font-sans">
        <Header />
        <main className="pt-16"> {/* Padding-top based on fixed header height */}
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
