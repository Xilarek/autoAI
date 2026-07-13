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
      { protocol: "https", hostname: "st.drom.ru" },
      { protocol: "https", hostname: "avatars.mds.yandex.net" },
      // Авито
      { protocol: "https", hostname: "www.avito.ru" },
      { protocol: "https", hostname: "avito.ru" },
      // Auto.ru
      { protocol: "https", hostname: "auto.ru" },
      { protocol: "https", hostname: "www.auto.ru" },
      // Для тестов (example.com)
      { protocol: "https", hostname: "example.com" },
      // Любой localhost для разработки
      { protocol: "http", hostname: "localhost" },
      { protocol: "https", hostname: "localhost" },
    ],
    // Разрешаем неоптимизированные изображения (если бэкенд возвращает прямые ссылки)
    unoptimized: false,
  },
}

module.exports = nextConfig
