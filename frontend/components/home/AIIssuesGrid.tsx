import { Card, CardContent } from "@/components/ui/card"
import { ImageOff, FileWarning, EyeOff, DollarSign, AlertTriangle, XCircle } from "lucide-react"

const issues = [
  { icon: ImageOff, text: "Скрытые дефекты на фото", color: "text-red-600" },
  { icon: FileWarning, text: "Редактирование фотографий", color: "text-orange-600" },
  { icon: EyeOff, text: "AI-генерация изображений", color: "text-yellow-600" },
  { icon: DollarSign, text: "Завышенная цена", color: "text-red-600" },
  { icon: AlertTriangle, text: "Несоответствие описания", color: "text-orange-600" },
  { icon: XCircle, text: "Подозрительные объявления", color: "text-red-600" },
]

export function AIIssuesGrid() {
  return (
    <div className="space-y-4">
      <h2 className="text-center text-2xl font-bold">Что находит наш AI?</h2>
      <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
        {issues.map((issue, index) => {
          const Icon = issue.icon

          return (
            <Card key={index} className="border-gray-200">
              <CardContent className="pt-4">
                <div className="flex items-center gap-3">
                  <Icon className={`h-5 w-5 ${issue.color}`} />
                  <span className="text-sm font-medium">{issue.text}</span>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
