import createMiddleware from 'next-intl/middleware';

export default createMiddleware({
  // A list of all locales that are supported
  locales: ['en', 'pt'],

  // Used when no locale matches
  defaultLocale: 'en',

  // Strategy for locale prefixing (optional)
  // 'as-needed': Only add prefix if locale is not the default
  // 'always': Always add the prefix (e.g., /en/about, /pt/about)
  // 'never': Don't add the prefix (requires careful routing setup)
  localePrefix: 'as-needed' 
});

export const config = {
  // Match only internationalized pathnames
  // Skip paths like /api, /_next, /_vercel, /favicon.ico, etc.
  matcher: ['/((?!api|_next|_vercel|.*\..*).*)']
};
