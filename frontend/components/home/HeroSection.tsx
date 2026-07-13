"use client"

import { BaseButton } from "@/components/common/BaseButton"
import { Search, TrendingUp, Zap } from "lucide-react"
import { useRouter } from "next/navigation"

export function HeroSection() {
  const router = useRouter()

  return (
    <div className="space-y-4 py-8 text-center">
      <div className="inline-flex items-center gap-2 rounded-full bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700">
        <Zap className="h-4 w-4" />
        AI-powered подбор автомобилей
      </div>
      <h1 className="text-4xl font-bold text-gray-900">
        Найдите идеальный автомобиль
        <br />
        <span className="text-blue-600">с помощью искусственного интеллекта</span>
      </h1>
      <p className="mx-auto max-w-3xl text-xl text-gray-600">
        Автоматический поиск по всем площадкам, анализ фотографий и умный рейтинг
      </p>
      <div className="flex justify-center gap-4 pt-4">
        <BaseButton
          size="lg"
          onClick={() => router.push("/search")}
          className="bg-blue-600 hover:bg-blue-700"
          icon={<Search className="h-5 w-5" />}
        >
          Начать поиск
        </BaseButton>
        <BaseButton
          size="lg"
          variant="outline"
          onClick={() => router.push("/listings")}
          icon={<TrendingUp className="h-5 w-5" />}
        >
          Смотреть объявления
        </BaseButton>
      </div>
    </div>
  )
}
