import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "www.caadf.org.br",
        port: "",
        pathname: "/wp-content/uploads/*",
        search: "",
      },
      {
        protocol: "https",
        hostname: "caadf.org.br",
        port: "",
        pathname: "/wp-content/uploads/*",
        search: "",
      },
    ],
  },
};

export default nextConfig;
