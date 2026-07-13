"use client"

import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { BaseButton } from "@/components/shared/buttons/BaseButton"
import { OptimizedImage } from "@/components/shared/media/OptimizedImage"
import { VerdictBadge } from "@/components/features/ai/VerdictBadge"
import { formatPrice } from "@/lib/utils"
import { ExternalLink, MapPin, Gauge } from "lucide-react"
import { useRouter } from "next/navigation"
import type { KeyboardEvent } from "react"
import type { ListingOut } from "@/types/api"

interface CarCardProps {
  car: ListingOut
}

export function CarCard({ car }: CarCardProps) {
  const router = useRouter()

  // Обработчик клика по всей карточке
  const handleCardClick = () => {
    router.push(`/listings/${car.id}`)
  }

  // Обработчик клавиатуры для доступности (Enter или Пробел)
  const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault()
      handleCardClick()
    }
  }

  // Безопасное получение первого фото
  const imageUrl = Array.isArray(car.photos) && car.photos.length > 0 ? car.photos[0] : null

  return (
    <Card
      className="group relative flex flex-col hover:shadow-lg transition-all duration-200 cursor-pointer border-gray-200 overflow-hidden focus-within:ring-2 focus-within:ring-blue-500 focus-within:ring-offset-2 outline-none"
      onClick={handleCardClick}
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role="article"
      aria-label={`Объявление: ${car.brand} ${car.model} ${car.year} года, цена ${formatPrice(car.price)}`}
    >
      {/* Изображение */}
      <div className="relative h-48 w-full bg-gray-100">
        <OptimizedImage
          src={imageUrl}
          alt={`${car.brand} ${car.model} ${car.year} года выпуска`}
          fill
          className="group-hover:scale-105 transition-transform duration-300"
        />

        {/* Бейдж вердикта AI */}
        {car.verdict && (
          <div className="absolute top-3 right-3">
            <VerdictBadge verdict={car.verdict} />
          </div>
        )}
      </div>

      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0 flex-1">
            <h3 className="font-bold text-lg text-gray-900 group-hover:text-blue-600 transition-colors line-clamp-1">
              {car.brand} {car.model}
            </h3>
            <p className="text-sm text-gray-500">
              {car.year} год • {car.source ? car.source.toUpperCase() : "Не указано"}
            </p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4 flex-1 flex flex-col">
        {/* Цена и рыночная цена */}
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold text-gray-900">{formatPrice(car.price)}</span>
          {car.market_price && car.market_price !== car.price && (
            <span 
              className="text-sm text-gray-400 line-through" 
              aria-label={`Рыночная цена: ${formatPrice(car.market_price)}`}
            >
              {formatPrice(car.market_price)}
            </span>
          )}
        </div>

        {/* Характеристики */}
        <div className="flex flex-wrap gap-3 text-sm text-gray-600">
          {car.mileage && (
            <div 
              className="flex items-center gap-1.5 bg-gray-50 px-2 py-1 rounded-md" 
              aria-label={`Пробег: ${car.mileage.toLocaleString("ru-RU")} километров`}
            >
              <Gauge className="h-4 w-4 text-gray-500" aria-hidden="true" />
              <span>{car.mileage.toLocaleString("ru-RU")} км</span>
            </div>
          )}
          {car.region && (
            <div 
              className="flex items-center gap-1.5 bg-gray-50 px-2 py-1 rounded-md" 
              aria-label={`Регион: ${car.region}`}
            >
              <MapPin className="h-4 w-4 text-gray-500" aria-hidden="true" />
              <span className="line-clamp-1">{car.region}</span>
            </div>
          )}
        </div>

        {/* Кнопки действий (прижаты к низу карточки) */}
        <div className="pt-3 mt-auto border-t border-gray-100 flex gap-2">
          <BaseButton
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={(e) => {
              e.stopPropagation()
              router.push(`/listings/${car.id}`)
            }}
            aria-label={`Подробнее об автомобиле ${car.brand} ${car.model}`}
          >
            Подробнее
          </BaseButton>
          
          {car.url && (
            <BaseButton
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                window.open(car.url, "_blank", "noopener,noreferrer")
              }}
              aria-label="Открыть оригинальное объявление на внешнем сайте в новой вкладке"
              title="Открыть оригинальное объявление"
            >
              <ExternalLink className="h-4 w-4" aria-hidden="true" />
            </BaseButton>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
