"use client"

import { BaseButton } from "@/components/shared/buttons/BaseButton"
import { AlertTriangle, RefreshCw } from "lucide-react"

interface ErrorStateProps {
  title?: string
  description?: string
  onRetry: () => void
  isRetrying?: boolean
}

export function ErrorState({
  title = "Что-то пошло не так",
  description = "Не удалось загрузить данные. Проверьте подключение к интернету.",
  onRetry,
  isRetrying,
}: ErrorStateProps) {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center gap-4 text-center">
      <div className="rounded-full bg-red-50 p-4">
        <AlertTriangle className="h-10 w-10 text-red-500" />
      </div>
      <h3 className="text-xl font-semibold text-gray-900">{title}</h3>
      <p className="max-w-md text-gray-500">{description}</p>
      <BaseButton
        onClick={onRetry}
        icon={<RefreshCw className={`h-4 w-4 ${isRetrying ? "animate-spin" : ""}`} />}
      >
        Попробовать снова
      </BaseButton>
    </div>
  )
}
