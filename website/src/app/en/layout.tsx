import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import React from 'react';

// Optional: If you have shared components like Header/Footer, import them here
// import Header from '@/components/layout/Header';
// import Footer from '@/components/layout/Footer';

interface EnLayoutProps {
  children: React.ReactNode;
}

export default async function EnLayout({ children }: EnLayoutProps) {
  // Providing all messages to the client
  // side is the easiest way to get started
  const messages = await getMessages();

  return (
    <NextIntlClientProvider locale="en" messages={messages}>
      {/* If using Header/Footer, place them outside/inside provider as needed */}
      {/* <Header /> */}
      {children}
      {/* <Footer /> */}
    </NextIntlClientProvider>
  );
}