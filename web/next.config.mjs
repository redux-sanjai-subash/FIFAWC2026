/** @type {import('next').NextConfig} */
const API_ORIGIN = process.env.API_ORIGIN || "http://127.0.0.1:8082";

const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    // The browser only ever talks to the Next.js origin, so the Flask session
    // cookie behaves like a first-party cookie. All /api traffic is proxied to
    // the Flask service.
    return [
      {
        source: "/api/:path*",
        destination: `${API_ORIGIN}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
