import { Inbox } from "lucide-react"

interface EmptyStateProps {
  title?: string
  description?: string
  action?: React.ReactNode
}

export function EmptyState({
  title = "Ничего не найдено",
  description = "Попробуйте изменить параметры поиска",
  action,
}: EmptyStateProps) {
  return (
    <div className="rounded-lg border border-dashed border-gray-300 bg-gray-50 py-16 text-center">
      <Inbox className="mx-auto mb-4 h-12 w-12 text-gray-400" />
      <p className="text-lg font-medium text-gray-500">{title}</p>
      <p className="mb-6 mt-2 text-sm text-gray-400">{description}</p>
      {action}
    </div>
  )
}
