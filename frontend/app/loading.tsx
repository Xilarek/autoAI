import { CarCardSkeleton } from "@/components/features/car/CarCardSkeleton"

export default function Loading() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="flex items-center justify-between">
        <div className="h-8 w-48 rounded bg-gray-200" />
        <div className="h-10 w-32 rounded bg-gray-200" />
      </div>
      {/* Имитируем сетку карточек */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <CarCardSkeleton key={i} />
        ))}
      </div>
    </div>
  )
}
