"use client"

import { BaseButton } from "@/components/common/BaseButton"

interface PaginationProps {
  currentPage: number
  totalPages: number
  isFetching?: boolean
  onPageChange: (page: number) => void
}

export function Pagination({ currentPage, totalPages, isFetching, onPageChange }: PaginationProps) {
  if (totalPages <= 1) return null

  return (
    <div className="flex items-center justify-center gap-3 pt-6 border-t">
      <BaseButton
        variant="outline"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1 || isFetching}
      >
        Назад
      </BaseButton>
      
      <span className="text-sm font-medium text-gray-600 px-4 min-w-[120px] text-center">
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
