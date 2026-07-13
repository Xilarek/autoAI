import { Inbox } from "lucide-react"

interface EmptyStateProps {
  title?: string
  description?: string
  action?: React.ReactNode
}

export function EmptyState({ 
  title = "Ничего не найдено", 
  description = "Попробуйте изменить параметры поиска",
  action 
}: EmptyStateProps) {
  return (
    <div className="text-center py-16 bg-gray-50 rounded-lg border border-dashed border-gray-300">
      <Inbox className="h-12 w-12 text-gray-400 mx-auto mb-4" />
      <p className="text-gray-500 text-lg font-medium">{title}</p>
      <p className="text-gray-400 text-sm mt-2 mb-6">{description}</p>
      {action}
    </div>
  )
}
