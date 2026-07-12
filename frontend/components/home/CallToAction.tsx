"use client"

import { Card, CardContent } from "@/components/ui/card"
import { BaseButton } from "@/components/common/BaseButton"
import { Search, ExternalLink } from "lucide-react"
import { useRouter } from "next/navigation"

export function CallToAction() {
  const router = useRouter()

  return (
    <Card className="bg-gradient-to-r from-blue-600 to-purple-600 text-white border-0">
      <CardContent className="pt-8 pb-8">
        <div className="text-center space-y-4">
          <h2 className="text-2xl font-bold">Готовы найти свой идеальный автомобиль?</h2>
          <p className="text-blue-100">Запустите поиск и получите умный анализ</p>
          <div className="flex gap-4 justify-center pt-4">
            <BaseButton 
              size="lg" 
              variant="secondary" 
              onClick={() => router.push("/search")}
              icon={<Search className="h-5 w-5" />}
            >
              Запустить поиск
            </BaseButton>
            <BaseButton 
              size="lg" 
              variant="outline" 
              className="border-white text-black hover:bg-white hover:text-blue-600 transition-colors"
              onClick={() => router.push("/listings")}
              icon={<ExternalLink className="h-5 w-5" />}
            >
              Смотреть объявления
            </BaseButton>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
