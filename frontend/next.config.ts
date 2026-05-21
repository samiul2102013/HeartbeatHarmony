import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    images: {
        unoptimized: true,
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
            }
        ],
        
        
    },
    reactCompiler: true,
};

export default nextConfig;
