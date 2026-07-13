"use client"

import { useQuery } from "@tanstack/react-query"
import { carsApi } from "@/lib/api/cars"
import { CarCard } from "@/components/features/car/CarCard"
import { CarCardSkeleton } from "@/components/features/car/CarCardSkeleton"
import { Pagination } from "@/components/shared/navigation/Pagination"
import { EmptyState } from "@/components/shared/feedback/EmptyState"
import { ErrorState } from "@/components/shared/feedback/ErrorState"
import { BaseButton } from "@/components/shared/buttons/BaseButton"
import { Filter, RefreshCw } from "lucide-react"
import { useState } from "react"

export default function ListingsClient() {
  const [page, setPage] = useState(1)
  const limit = 12

  const { data, isLoading, error, refetch, isFetching } = useQuery({
    queryKey: ["listings", page],
    queryFn: async () => {
      const response = await carsApi.getList({
        skip: (page - 1) * limit,
        limit,
      })
      return response.data
    },
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 animate-pulse rounded bg-gray-200" />
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <CarCardSkeleton key={i} />
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return <ErrorState onRetry={() => refetch()} isRetrying={isFetching} />
  }

  // Умная нормализация данных: работает и с массивом, и с объектом пагинации
  const cars = Array.isArray(data) ? data : data?.reports || []
  const total = Array.isArray(data) ? data.length : data?.total || 0
  const perPage = Array.isArray(data) ? limit : data?.per_page || limit
  const totalPages = Math.max(1, Math.ceil(total / perPage))

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Объявления</h1>
          <p className="mt-1 text-sm text-gray-500">
            Найдено: <span className="font-semibold text-gray-900">{total}</span> автомобилей
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

      {cars.length === 0 ? (
        <EmptyState
          title="Объявлений пока нет"
          description="Запустите поиск, чтобы добавить новые предложения"
        />
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {cars.map((car) => (
            <CarCard key={car.id} car={car} />
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <Pagination
          currentPage={page}
          totalPages={totalPages}
          isFetching={isFetching}
          onPageChange={setPage}
        />
      )}
    </div>
  )
}
