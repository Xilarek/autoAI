"use client"

import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { BaseButton } from "@/components/common/BaseButton"
import { ExternalLink, MapPin, Gauge } from "lucide-react"
import { useRouter } from "next/navigation"
import type { ListingOut } from "@/types/api"

interface CarCardProps {
  car: ListingOut
}

const VERDICT_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  "ЗВОНИТЬ": { bg: "bg-green-100", text: "text-green-700", border: "border-green-200" },
  "ТОРГОВАТЬСЯ": { bg: "bg-blue-100", text: "text-blue-700", border: "border-blue-200" },
  "ДУМАТЬ": { bg: "bg-yellow-100", text: "text-yellow-700", border: "border-yellow-200" },
  "БЕЖАТЬ": { bg: "bg-red-100", text: "text-red-700", border: "border-red-200" },
}

export function CarCard({ car }: CarCardProps) {
  const router = useRouter()
  const verdict = car.verdict || "ДУМАТЬ"
  const colors = VERDICT_COLORS[verdict] || VERDICT_COLORS["ДУМАТЬ"]

  const formatPrice = (price: number) =>
    new Intl.NumberFormat("ru-RU", {
      style: "currency",
      currency: "RUB",
      maximumFractionDigits: 0,
    }).format(price)

  return (
    <Card
      className="group hover:shadow-lg transition-all duration-200 cursor-pointer border-gray-200 overflow-hidden"
      onClick={() => router.push(`/listings/${car.id}`)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div>
            <h3 className="font-bold text-lg text-gray-900 group-hover:text-blue-600 transition-colors line-clamp-1">
              {car.brand} {car.model}
            </h3>
            <p className="text-sm text-gray-500">
              {car.year} год • {car.source ? car.source.toUpperCase() : "Не указано"}
            </p>
          </div>
          <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${colors.bg} ${colors.text} ${colors.border}`}>
            {verdict}
          </span>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold text-gray-900">{formatPrice(car.price)}</span>
          {car.market_price && car.market_price !== car.price && (
            <span className="text-sm text-gray-400 line-through">{formatPrice(car.market_price)}</span>
          )}
        </div>

        <div className="flex flex-wrap gap-3 text-sm text-gray-600">
          {car.mileage && (
            <div className="flex items-center gap-1.5 bg-gray-50 px-2 py-1 rounded-md">
              <Gauge className="h-4 w-4 text-gray-500" />
              <span>{car.mileage.toLocaleString("ru-RU")} км</span>
            </div>
          )}
          {car.region && (
            <div className="flex items-center gap-1.5 bg-gray-50 px-2 py-1 rounded-md">
              <MapPin className="h-4 w-4 text-gray-500" />
              <span className="line-clamp-1">{car.region}</span>
            </div>
          )}
        </div>

        <div className="pt-3 border-t border-gray-100 flex gap-2">
          <BaseButton
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={(e) => {
              e.stopPropagation()
              router.push(`/listings/${car.id}`)
            }}
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
              title="Открыть оригинальное объявление"
            >
              <ExternalLink className="h-4 w-4" />
            </BaseButton>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
