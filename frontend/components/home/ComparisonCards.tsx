"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { BaseButton } from "@/components/common/BaseButton"
import { CheckCircle2, AlertTriangle, XCircle, ImageOff, EyeOff, DollarSign, FileWarning } from "lucide-react"
import { useRouter } from "next/navigation"

export function ComparisonCards() {
  const router = useRouter()

  return (
    <div className="grid gap-6 md:grid-cols-2">
      {/* Лучшие результаты */}
      <Card className="border-green-300 bg-gradient-to-br from-green-50 to-emerald-50">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-600 rounded-lg">
              <CheckCircle2 className="h-6 w-6 text-white" />
            </div>
            <div>
              <CardTitle className="text-green-900">✅ Лучшие результаты</CardTitle>
              <CardDescription>Объявления с вердиктом "ЗВОНИТЬ" и "ТОРГОВАТЬСЯ"</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-3 flex flex-col h-full">
          <div className="space-y-2 flex-1">
            <div className="flex items-start gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5" />
              <div>
                <p className="font-medium text-green-900">Чистые фотографии</p>
                <p className="text-sm text-green-700">Без следов редактирования</p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5" />
              <div>
                <p className="font-medium text-green-900">Рыночная цена</p>
                <p className="text-sm text-green-700">Соответствует состоянию</p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5" />
              <div>
                <p className="font-medium text-green-900">Полное описание</p>
                <p className="text-sm text-green-700">Все детали честно указаны</p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5" />
              <div>
                <p className="font-medium text-green-900">Хорошее состояние</p>
                <p className="text-sm text-green-700">Минимум дефектов</p>
              </div>
            </div>
          </div>
          <BaseButton 
            onClick={() => router.push("/listings?verdict=ЗВОНИТЬ")} 
            className="w-full bg-green-600 hover:bg-green-700 mt-auto"
          >
            Смотреть лучшие предложения
          </BaseButton>
        </CardContent>
      </Card>

      {/* Проблемные объявления */}
      <Card className="border-red-300 bg-gradient-to-br from-red-50 to-orange-50">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-600 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-white" />
            </div>
            <div>
              <CardTitle className="text-red-900">⚠️ Проблемные объявления</CardTitle>
              <CardDescription>Объявления с вердиктом "ДУМАТЬ" и "БЕЖАТЬ"</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-3 flex flex-col h-full">
          <div className="space-y-2 flex-1">
            <div className="flex items-start gap-2">
              <XCircle className="h-5 w-5 text-red-600 mt-0.5" />
              <div>
                <p className="font-medium text-red-900">Скрытые дефекты</p>
                <p className="text-sm text-red-700">Повреждения, коррозия, царапины</p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <ImageOff className="h-5 w-5 text-red-600 mt-0.5" />
              <div>
                <p className="font-medium text-red-900">Редактирование фото</p>
                <p className="text-sm text-red-700">Для сокрытия проблем</p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <EyeOff className="h-5 w-5 text-orange-600 mt-0.5" />
              <div>
                <p className="font-medium text-red-900">AI-генерация</p>
                <p className="text-sm text-red-700">Сильно отредактированы</p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <DollarSign className="h-5 w-5 text-red-600 mt-0.5" />
              <div>
                <p className="font-medium text-red-900">Завышенная цена</p>
                <p className="text-sm text-red-700">На 15-30% выше рынка</p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <FileWarning className="h-5 w-5 text-orange-600 mt-0.5" />
              <div>
                <p className="font-medium text-red-900">Несоответствие описания</p>
                <p className="text-sm text-red-700">Не совпадает с фото</p>
              </div>
            </div>
          </div>
          <BaseButton 
            onClick={() => router.push("/listings?verdict=БЕЖАТЬ")} 
            variant="outline" 
            className="w-full border-red-300 text-red-700 hover:bg-red-100 mt-auto"
          >
            Посмотреть проблемные объявления
          </BaseButton>
        </CardContent>
      </Card>
    </div>
  )
}
