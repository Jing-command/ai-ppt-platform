/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async redirects() {
    return [
      {
        source: '/',
        destination: '/login',
        permanent: false,
      },
      {
        source: '/app',
        destination: '/app/dashboard',
        permanent: false,
      },
    ];
  },
};

module.exports = nextConfig;
