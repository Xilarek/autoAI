/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/:path*`,
      },
    ]
  },
  reactStrictMode: true,
  images: {
    remotePatterns: [
      // Дром
      { protocol: "https", hostname: "auto.drom.ru" },
      { protocol: "https", hostname: "st.drom.ru" }, // часто фото хранятся на поддоменах st
      // Авито
      { protocol: "https", hostname: "www.avito.ru" },
      { protocol: "https", hostname: "avatars.mds.yandex.net" }, // Авито использует Яндекс.Картинки для заглушек/фото
      // Auto.ru
      { protocol: "https", hostname: "auto.ru" },
      { protocol: "https", hostname: "www.auto.ru" },
      { protocol: "https", hostname: "avatars.mds.yandex.net" }, // Auto.ru тоже использует Яндекс
    ],
  },
}

module.exports = nextConfig