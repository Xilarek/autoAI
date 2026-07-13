import Link from "next/link"
import { BaseButton } from "@/components/shared/buttons/BaseButton"
import { Home, Search } from "lucide-react"

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center space-y-6 text-center">
      <div className="rounded-full bg-gray-100 p-6">
        <Search className="h-16 w-16 text-gray-400" />
      </div>
      <div className="space-y-2">
        <h1 className="text-4xl font-bold text-gray-900">404</h1>
        <h2 className="text-xl font-semibold text-gray-700">Объявление не найдено</h2>
        <p className="max-w-md text-gray-500">
          Возможно, автомобиль уже продан, удален продавцом или вы перешли по неверной ссылке.
        </p>
      </div>
      <div className="flex gap-4">
        <Link href="/">
          <BaseButton variant="outline" icon={<Home className="h-4 w-4" />}>
            На главную
          </BaseButton>
        </Link>
        <Link href="/listings">
          <BaseButton icon={<Search className="h-4 w-4" />}>К списку объявлений</BaseButton>
        </Link>
      </div>
    </div>
  )
}
