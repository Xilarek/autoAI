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
  description: "AI-анализ объявлений на Дром, Авито и Auto.ru. Поиск скрытых дефектов, проверка рыночной цены и умные вердикты.",
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

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru">
      <body className={inter.className}>
        <QueryProvider>
          <div className="min-h-screen bg-gray-50 flex flex-col">
            <header className="border-b bg-white sticky top-0 z-50">
              <div className="container mx-auto px-4 py-4 flex items-center justify-between">
                <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
                  <span className="text-xl">🚗</span>
                  <span className="text-xl font-bold text-gray-900">AutoAI</span>
                </Link>
                
                <nav className="flex gap-6">
                  <Link href="/listings" className="text-gray-600 hover:text-blue-600 transition-colors">
                    Объявления
                  </Link>
                  <Link href="/search" className="text-gray-600 hover:text-blue-600 transition-colors">
                    Поиск
                  </Link>
                  <Link href="/tasks" className="text-gray-600 hover:text-blue-600 transition-colors">
                    Задачи
                  </Link>
                </nav>
              </div>
            </header>
            <main className="container mx-auto px-4 py-6 flex-grow">
              {children}
            </main>
            <footer className="border-t mt-auto py-6 text-center text-gray-500 text-sm">
              © {new Date().getFullYear()} AutoAI. Все права защищены.
            </footer>
          </div>
        </QueryProvider>
      </body>
    </html>
  )
}
