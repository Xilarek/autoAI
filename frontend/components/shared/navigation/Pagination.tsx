"use client"

import { BaseButton } from "@/components/shared/buttons/BaseButton"

interface PaginationProps {
  currentPage: number
  totalPages: number
  isFetching?: boolean
  onPageChange: (page: number) => void
}

export function Pagination({ currentPage, totalPages, isFetching, onPageChange }: PaginationProps) {
  if (totalPages <= 1) return null

  return (
    <div className="flex items-center justify-center gap-3 border-t pt-6">
      <BaseButton
        variant="outline"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1 || isFetching}
      >
        Назад
      </BaseButton>

      <span className="min-w-[120px] px-4 text-center text-sm font-medium text-gray-600">
        Страница {currentPage} из {totalPages}
      </span>

      <BaseButton
        variant="outline"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages || isFetching}
      >
        Вперёд
      </BaseButton>
    </div>
  )
}
