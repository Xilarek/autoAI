"use client"

import { useRouter } from "next/navigation"
import { BaseButton } from "@/components/shared/buttons/BaseButton"
import { OptimizedImage } from "@/components/shared/media/OptimizedImage"
import { VerdictBadge } from "@/components/features/ai/VerdictBadge"
import { formatPrice } from "@/lib/utils"
import {
  ArrowLeft,
  ExternalLink,
  Gauge,
  MapPin,
  Calendar,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  Droplets,
  Zap,
  Settings,
  Car,
} from "lucide-react"
import type { ListingOut } from "@/types/api"

interface CarDetailsClientProps {
  car: ListingOut
}

export default function CarDetailsClient({ car }: CarDetailsClientProps) {
  const router = useRouter()

  const photos = Array.isArray(car.photos) && car.photos.length > 0 ? car.photos : [null]
  const mainPhoto = photos[0]
  const price = car.price_rub || 0
  const marketPrice = car.fair_price
  const verdict = car.ai_verdict

  return (
    <div className="space-y-8 duration-500 animate-in fade-in">
      {/* Навигация назад */}
      <BaseButton
        variant="ghost"
        onClick={() => router.back()}
        icon={<ArrowLeft className="h-4 w-4" />}
        className="pl-0 transition-all hover:pl-2"
      >
        Назад к списку
      </BaseButton>

      <div className="grid gap-8 lg:grid-cols-3">
        {/* ЛЕВАЯ КОЛОНКА: Фото, Описание и Характеристики */}
        <div className="space-y-6 lg:col-span-2">
          {/* Галерея */}
          <div className="relative aspect-video w-full overflow-hidden rounded-xl border border-gray-200 bg-gray-100">
            <OptimizedImage
              src={mainPhoto}
              alt={`${car.brand} ${car.model} ${car.year}`}
              fill
              className="object-cover"
              priority={true} // Важно для LCP (Largest Contentful Paint)
            />
          </div>

          {/* Заголовок и цена */}
          <div className="space-y-4">
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-3xl font-bold text-gray-900">
                {car.brand} {car.model}
              </h1>
              {verdict && <VerdictBadge verdict={verdict} className="px-3 py-1.5 text-sm" />}
            </div>

            <div className="flex items-baseline gap-3">
              <span className="text-4xl font-extrabold text-gray-900">{formatPrice(price)}</span>
              {marketPrice && marketPrice !== price && (
                <span className="text-lg text-gray-400 line-through">
                  Рынок: {formatPrice(marketPrice)}
                </span>
              )}
            </div>

            {/* Сетка характеристик */}
            <div className="grid grid-cols-2 gap-4 border-t border-gray-100 pt-4 sm:grid-cols-4">
              <div className="flex flex-col gap-1">
                <span className="text-xs uppercase tracking-wider text-gray-500">Год</span>
                <div className="flex items-center gap-2 font-medium text-gray-900">
                  <Calendar className="h-4 w-4 text-gray-400" aria-hidden="true" />
                  {car.year}
                </div>
              </div>
              {car.mileage && (
                <div className="flex flex-col gap-1">
                  <span className="text-xs uppercase tracking-wider text-gray-500">Пробег</span>
                  <div className="flex items-center gap-2 font-medium text-gray-900">
                    <Gauge className="h-4 w-4 text-gray-400" aria-hidden="true" />
                    {car.mileage.toLocaleString("ru-RU")} км
                  </div>
                </div>
              )}
              {car.engine_volume && (
                <div className="flex flex-col gap-1">
                  <span className="text-xs uppercase tracking-wider text-gray-500">Двигатель</span>
                  <div className="flex items-center gap-2 font-medium text-gray-900">
                    <Droplets className="h-4 w-4 text-gray-400" aria-hidden="true" />
                    {car.engine_volume} л, {car.fuel_type || "Н/Д"}
                  </div>
                </div>
              )}
              {car.transmission && (
                <div className="flex flex-col gap-1">
                  <span className="text-xs uppercase tracking-wider text-gray-500">КПП</span>
                  <div className="flex items-center gap-2 font-medium text-gray-900">
                    <Settings className="h-4 w-4 text-gray-400" aria-hidden="true" />
                    {car.transmission}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Описание */}
          {car.description && (
            <div className="prose prose-sm max-w-none rounded-xl border border-gray-200 bg-white p-6 text-gray-700">
              <h3 className="mb-3 flex items-center gap-2 text-lg font-semibold text-gray-900">
                <Car className="h-5 w-5 text-blue-600" />
                Описание продавца
              </h3>
              <p className="whitespace-pre-wrap leading-relaxed">{car.description}</p>
            </div>
          )}
        </div>

        {/* ПРАВАЯ КОЛОНКА: AI-Отчет и Действия (Липкая) */}
        <div className="space-y-6">
          <div className="sticky top-24 space-y-6">
            {/* Блок действий */}
            <div className="space-y-4 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
              <h3 className="font-semibold text-gray-900">Связаться с продавцом</h3>
              <BaseButton
                className="w-full"
                size="lg"
                onClick={() => car.url && window.open(car.url, "_blank", "noopener,noreferrer")}
                disabled={!car.url}
                icon={<ExternalLink className="h-4 w-4" />}
              >
                Перейти к объявлению
              </BaseButton>
              <p className="text-center text-xs text-gray-500">
                Вы будете перенаправлены на {car.source || "сайт-источник"}
              </p>
            </div>

            {/* AI-Анализ */}
            <div className="space-y-4 rounded-xl border border-blue-100 bg-blue-50/50 p-6">
              <div className="flex items-center gap-2">
                <ShieldAlert className="h-5 w-5 text-blue-600" />
                <h3 className="font-semibold text-blue-900">AI-Анализ</h3>
              </div>

              {car.ai_summary ? (
                <p className="rounded-lg bg-blue-100/50 p-3 text-sm leading-relaxed text-blue-800">
                  {car.ai_summary}
                </p>
              ) : (
                <p className="text-sm italic text-blue-800">
                  Развернутый анализ пока не сгенерирован.
                </p>
              )}

              {car.ai_risks && car.ai_risks.length > 0 && (
                <div className="pt-2">
                  <h4 className="mb-3 flex items-center gap-2 text-sm font-semibold text-red-700">
                    <AlertTriangle className="h-4 w-4" />
                    Выявленные риски:
                  </h4>
                  <ul className="space-y-2">
                    {car.ai_risks.map((risk, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                        <AlertTriangle
                          className="mt-0.5 h-4 w-4 shrink-0 text-red-500"
                          aria-hidden="true"
                        />
                        <div className="flex-1">
                          <div className="font-semibold text-red-600">{risk.marker}</div>
                          <div className="text-xs text-gray-500">Уровень: {risk.level}</div>
                          <div className="mt-1">{risk.explanation}</div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {!car.ai_risks?.length && verdict === "ЗВОНИТЬ" && (
                <div className="border-t border-blue-200 pt-2">
                  <h4 className="mb-2 flex items-center gap-2 text-sm font-semibold text-green-700">
                    <CheckCircle2 className="h-4 w-4" />
                    Плюсы:
                  </h4>
                  <p className="text-sm text-gray-700">
                    Явных рисков не обнаружено. Цена соответствует рынку или ниже.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
