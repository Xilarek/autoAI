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
      // Извлекаем .data из ответа Axios, чтобы в компоненте data была типа ReportsResponse
      const response = await carsApi.getList({ 
        skip: (page - 1) * limit, 
        limit 
      })
      return response.data
    },
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-gray-200 rounded animate-pulse" />
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => <CarCardSkeleton key={i} />)}
        </div>
      </div>
    )
  }

  if (error) {
    return <ErrorState onRetry={() => refetch()} isRetrying={isFetching} />
  }

  // Теперь data имеет тип ReportsResponse, и TypeScript доволен
  const totalPages = data ? Math.ceil(data.total / data.per_page) : 1

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
          <BaseButton variant="outline" icon={<Filter className="h-4 w-4" />}>Фильтры</BaseButton>
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
        <EmptyState 
          title="Объявлений пока нет" 
          description="Запустите поиск, чтобы добавить новые предложения" 
        />
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {data.reports.map((car) => (
            <CarCard key={car.id} car={car} />
          ))}
        </div>
      )}

      <Pagination 
        currentPage={page} 
        totalPages={totalPages} 
        isFetching={isFetching}
        onPageChange={setPage} 
      />
    </div>
  )
}
