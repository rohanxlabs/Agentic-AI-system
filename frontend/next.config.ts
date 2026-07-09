import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  distDir: '.next',
  allowedDevOrigins: ['127.0.0.1'],
  turbopack: {
    root: __dirname,
  },
};

export default nextConfig;