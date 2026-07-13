"use client"

import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { VERDICT_CONFIG } from "@/lib/constants"
import { formatPrice } from "@/lib/utils"
import { ExternalLink, MapPin } from "lucide-react"
import type { ListingOut } from "@/types/api"
import { useRouter } from "next/navigation"

interface CarCardProps {
  car: ListingOut
}

export function CarCard({ car }: CarCardProps) {
  const router = useRouter()
  const verdict = car.verdict || "ДУМАТЬ"
  const config = VERDICT_CONFIG[verdict] || VERDICT_CONFIG["ДУМАТЬ"]

  return (
    <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => router.push(`/listings/${car.id}`)}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div>
            <h3 className="font-semibold text-lg">{car.brand} {car.model}</h3>
            <p className="text-sm text-gray-600">{car.year} год</p>
          </div>
          <Badge className={`${config.bg} ${config.color} border-0`}>
            {config.label}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-2xl font-bold text-gray-900">{formatPrice(car.price)}</span>
          {car.market_price && (
            <span className="text-sm text-gray-500 line-through">
              {formatPrice(car.market_price)}
            </span>
          )}
        </div>

        {car.mileage && (
          <div className="flex items-center text-sm text-gray-600">
            <MapPin className="h-4 w-4 mr-1" />
            {car.mileage.toLocaleString("ru-RU")} км
          </div>
        )}

        {car.region && (
          <div className="text-sm text-gray-600">📍 {car.region}</div>
        )}

        <div className="pt-2 border-t">
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              className="flex-1"
              onClick={(e) => {
                e.stopPropagation()
                router.push(`/listings/${car.id}`)
              }}
            >
              Подробнее
            </Button>
            {car.url && (
              <Button
                variant="outline"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation()
                  window.open(car.url, "_blank")
                }}
              >
                <ExternalLink className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
