import type { Metadata } from "next"
import { Inter } from "next/font/google"
import Link from "next/link"
import "./globals.css"
import { QueryProvider } from "@/providers/query-provider"

const inter = Inter({ subsets: ["latin", "cyrillic"] })

// Глобальные настройки SEO
export const metadata: Metadata = {
  title: {
    default: "AutoAI — Умный подбор авто",
    template: "%s | AutoAI", // Автоматически добавит " | AutoAI" к заголовкам страниц
  },
  description:
    "AI-анализ объявлений на Дром, Авито и Auto.ru. Поиск скрытых дефектов, проверка рыночной цены и умные вердикты.",
  keywords: ["авто", "покупка авто", "AI анализ", "Дром", "Авито", "Auto.ru", "подбор авто"],
  metadataBase: new URL("http://localhost:3000"), // Замените на ваш домен при деплое
  openGraph: {
    title: "AutoAI — Умный подбор авто",
    description: "Найдите идеальный автомобиль с помощью искусственного интеллекта",
    type: "website",
    locale: "ru_RU",
    siteName: "AutoAI",
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body className={inter.className}>
        <QueryProvider>
          <div className="flex min-h-screen flex-col bg-gray-50">
            <header className="sticky top-0 z-50 border-b bg-white">
              <div className="container mx-auto flex items-center justify-between px-4 py-4">
                <Link
                  href="/"
                  className="flex items-center gap-2 transition-opacity hover:opacity-80"
                >
                  <span className="text-xl">🚗</span>
                  <span className="text-xl font-bold text-gray-900">AutoAI</span>
                </Link>

                <nav className="flex gap-6">
                  <Link
                    href="/listings"
                    className="text-gray-600 transition-colors hover:text-blue-600"
                  >
                    Объявления
                  </Link>
                  <Link
                    href="/search"
                    className="text-gray-600 transition-colors hover:text-blue-600"
                  >
                    Поиск
                  </Link>
                  <Link
                    href="/tasks"
                    className="text-gray-600 transition-colors hover:text-blue-600"
                  >
                    Задачи
                  </Link>
                </nav>
              </div>
            </header>
            <main className="container mx-auto flex-grow px-4 py-6">{children}</main>
            <footer className="mt-auto border-t py-6 text-center text-sm text-gray-500">
              © {new Date().getFullYear()} AutoAI. Все права защищены.
            </footer>
          </div>
        </QueryProvider>
      </body>
    </html>
  )
}
