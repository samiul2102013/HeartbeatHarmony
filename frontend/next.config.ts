import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    images: {
        remotePatterns: [
            {
                protocol: "https",
                hostname: "www.figma.com",
                pathname: "/api/mcp/asset/**",
            },
            {
                protocol: "https",
                hostname: "unsplash.com",
                pathname: "/photos/**",
            },
            {
                protocol: "https",
                hostname: "images.unsplash.com",
                pathname: "/photo-**",
            },
            {
                protocol: "https",
                hostname: "res.cloudinary.com",
                pathname: "/photo/**",
            },
            {
                protocol: "https",
                hostname: "api.heartbeatharmony.tech",
                pathname: "/media/**",
            },
        ],
        formats: ['image/avif', 'image/webp'],
    },
    reactCompiler: true,
};

export default nextConfig;
