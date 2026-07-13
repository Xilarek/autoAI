"use client"

import { useQuery } from "@tanstack/react-query"
import { carsApi } from "@/lib/api/cars"
import { CarCard } from "@/components/features/car/CarCard"
import { CarCardSkeleton } from "@/components/features/car/CarCardSkeleton"
import { BaseButton } from "@/components/common/BaseButton"
import { RefreshCw, Filter } from "lucide-react"
import { useState } from "react"

export default function ListingsClient() {
  const [filters, setFilters] = useState({
    skip: 0,
    limit: 12,
    sort_by: "created_at" as const,
    sort_order: "desc" as const,
  })

  const { data, isLoading, error, refetch, isFetching } = useQuery({
    queryKey: ["listings", filters],
    queryFn: () => carsApi.getList(filters),
  })

  // 1. Состояние загрузки (Скелетоны)
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="h-8 w-48 bg-gray-200 rounded animate-pulse" />
          <div className="h-10 w-32 bg-gray-200 rounded animate-pulse" />
        </div>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <CarCardSkeleton key={i} />
          ))}
        </div>
      </div>
    )
  }

  // 2. Состояние ошибки
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-4 text-center">
        <h3 className="text-xl font-semibold text-gray-900">Не удалось загрузить объявления</h3>
        <p className="text-gray-500 max-w-md">
          Проверьте подключение к интернету или попробуйте обновить страницу позже.
        </p>
        <BaseButton onClick={() => refetch()} icon={<RefreshCw className="h-4 w-4" />}>
          Попробовать снова
        </BaseButton>
      </div>
    )
  }

  const totalPages = data ? Math.ceil(data.total / data.per_page) : 1
  const currentPage = Math.floor(filters.skip / filters.limit) + 1

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Объявления</h1>
          <p className="text-gray-500 text-sm mt-1">
            Найдено: <span className="font-semibold text-gray-900">{data?.total || 0}</span> автомобилей
          </p>
        </div>
        <div className="flex gap-2">
          <BaseButton variant="outline" icon={<Filter className="h-4 w-4" />}>
            Фильтры
          </BaseButton>
          <BaseButton 
            variant="outline" 
            icon={<RefreshCw className={`h-4 w-4 ${isFetching ? "animate-spin" : ""}`} />}
            onClick={() => refetch()}
          >
            Обновить
          </BaseButton>
        </div>
      </div>

      {!data?.reports?.length ? (
        <div className="text-center py-16 bg-gray-50 rounded-lg border border-dashed border-gray-300">
          <p className="text-gray-500 text-lg font-medium">Объявлений пока нет</p>
          <p className="text-gray-400 text-sm mt-2">Запустите поиск, чтобы добавить новые предложения</p>
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {data?.reports.map((car) => (
            <CarCard key={car.id} car={car} />
          ))}
        </div>
      )}

      {data && totalPages > 1 && (
        <div className="flex items-center justify-center gap-3 pt-6 border-t">
          <BaseButton
            variant="outline"
            onClick={() => setFilters({ ...filters, skip: Math.max(0, filters.skip - filters.limit) })}
            disabled={currentPage === 1 || isFetching}
          >
            Назад
          </BaseButton>
          <span className="text-sm font-medium text-gray-600 px-4">
            Страница {currentPage} из {totalPages}
          </span>
          <BaseButton
            variant="outline"
            onClick={() => setFilters({ ...filters, skip: filters.skip + filters.limit })}
            disabled={currentPage === totalPages || isFetching}
          >
            Вперёд
          </BaseButton>
        </div>
      )}
    </div>
  )
}
