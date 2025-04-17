import { getRequestConfig } from 'next-intl/server';
import { notFound } from 'next/navigation';

const locales = ['en', 'pt'];

export default getRequestConfig(async ({ locale }) => {
  // Validate that the incoming `locale` parameter is valid
  if (!locale || !locales.includes(locale as string)) notFound();

  return {
    locale: locale as string,
    // Adjust the import path relative to the new file location (root)
    messages: (await import(`./src/locales/${locale}/common.json`)).default
  };
});
