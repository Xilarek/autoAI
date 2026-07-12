import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { QueryProvider } from "@/providers/query-provider"

const inter = Inter({ subsets: ["latin", "cyrillic"] })

export const metadata: Metadata = {
  title: "AutoAI — Умный подбор авто",
  description: "AI-анализ объявлений, проверка рисков и рыночных цен",
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
          <div className="min-h-screen bg-gray-50">
            <header className="border-b bg-white">
              <div className="container mx-auto px-4 py-4 flex items-center justify-between">
                <h1 className="text-xl font-bold text-gray-900">🚗 AutoAI</h1>
                <nav className="flex gap-4">
                  <a href="/listings" className="text-gray-600 hover:text-blue-600">Объявления</a>
                  <a href="/search" className="text-gray-600 hover:text-blue-600">Поиск</a>
                  <a href="/tasks" className="text-gray-600 hover:text-blue-600">Задачи</a>
                </nav>
              </div>
            </header>
            <main className="container mx-auto px-4 py-6">
              {children}
            </main>
            <footer className="border-t mt-12 py-6 text-center text-gray-500 text-sm">
              © {new Date().getFullYear()} AutoAI. Backend: FastAPI + Celery. Frontend: Next.js 14
            </footer>
          </div>
        </QueryProvider>
      </body>
    </html>
  )
}
