import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Search, ScanSearch, ShieldCheck, Brain, Sparkles, CheckCircle2 } from "lucide-react"

const features = [
  {
    icon: Search,
    title: "🔍 Поиск по всем площадкам",
    description: "Auto.ru, Авито и Дром одновременно",
    color: "blue",
  },
  {
    icon: ScanSearch,
    title: "🔬 AI-анализ фотографий",
    description: "Дефекты, повреждения, следы ремонта",
    color: "purple",
  },
  {
    icon: ShieldCheck,
    title: "🛡️ Обнаружение подделок",
    description: "Редактирование и AI-генерации",
    color: "red",
  },
  {
    icon: Brain,
    title: "🧠 Умный рейтинг",
    description: "Сотни факторов для анализа",
    color: "green",
  },
  {
    icon: Sparkles,
    title: "✨ AI-вердикты",
    description: "ЗВОНИТЬ / ТОРГОВАТЬСЯ / ДУМАТЬ / БЕЖАТЬ",
    color: "yellow",
  },
  {
    icon: CheckCircle2,
    title: "✅ Проверка соответствия",
    description: "Описание ↔ Фото",
    color: "indigo",
  },
]

const colorMap: Record<string, { border: string; bg: string; iconBg: string }> = {
  blue: { border: "border-blue-200", bg: "bg-blue-50/50", iconBg: "bg-blue-600" },
  purple: { border: "border-purple-200", bg: "bg-purple-50/50", iconBg: "bg-purple-600" },
  red: { border: "border-red-200", bg: "bg-red-50/50", iconBg: "bg-red-600" },
  green: { border: "border-green-200", bg: "bg-green-50/50", iconBg: "bg-green-600" },
  yellow: { border: "border-yellow-200", bg: "bg-yellow-50/50", iconBg: "bg-yellow-600" },
  indigo: { border: "border-indigo-200", bg: "bg-indigo-50/50", iconBg: "bg-indigo-600" },
}

export function FeaturesGrid() {
  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {features.map((feature, index) => {
        const colors = colorMap[feature.color]
        const Icon = feature.icon

        return (
          <Card key={index} className={`${colors.border} ${colors.bg}`}>
            <CardHeader>
              <div className="mb-2 flex items-center gap-3">
                <div className={`p-2 ${colors.iconBg} rounded-lg`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <CardTitle>{feature.title}</CardTitle>
              </div>
              <CardDescription>{feature.description}</CardDescription>
            </CardHeader>
          </Card>
        )
      })}
    </div>
  )
}
