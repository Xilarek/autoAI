import { carsApi } from "@/lib/api/cars"
import CarDetailsClient from "./CarDetailsClient"
import { notFound } from "next/navigation"
import type { Metadata } from "next"
import type { ListingOut } from "@/types/api"

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>
}): Promise<Metadata> {
  const { id } = await params

  try {
    const response = await carsApi.getById(Number(id))
    const car = response.data as ListingOut

    return {
      title: `${car.brand} ${car.model} (${car.year}) за ${car.price_rub.toLocaleString("ru-RU")} ₽ | AutoAI`,
      description: car.ai_summary || `Проверенное AI объявление ${car.brand} ${car.model}`,
      openGraph: {
        title: `${car.brand} ${car.model} (${car.year})`,
        description: `Цена: ${car.price_rub.toLocaleString("ru-RU")} ₽. Вердикт AI: ${car.ai_verdict || "Неизвестно"}`,
        type: "article",
      },
    }
  } catch (error) {
    return { title: "Автомобиль не найден | AutoAI" }
  }
}

export default async function CarDetailsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  console.log("🔍 [Server] Загрузка деталей для ID:", id)

  try {
    const response = await carsApi.getById(Number(id))
    console.log("📦 [Server] Сырой ответ API:", JSON.stringify(response.data, null, 2))

    // Проверяем, что это действительно объект автомобиля
    const car = response.data as ListingOut
    if (!car || !car.brand || !car.id) {
      console.error("❌ [Server] API вернул не объект автомобиля:", car)
      throw new Error("Invalid car data structure")
    }

    console.log("✅ [Server] Данные получены напрямую:", car.brand, car.model)
    return <CarDetailsClient car={car} />
  } catch (error) {
    console.error("❌ [Server] Ошибка прямого запроса /cars/{id}:", error)

    // Фоллбэк: пробуем найти в общем списке
    try {
      console.log("🔄 [Server] Пробуем фоллбэк через общий список...")
      const listResponse = await carsApi.getList({ limit: 100 })
      const listData = listResponse.data
      const cars = Array.isArray(listData) ? listData : listData?.reports || []
      const car = cars.find((c: any) => c.id === Number(id))

      if (car) {
        console.log("✅ [Server] Найдено через фоллбэк:", car.brand, car.model)
        return <CarDetailsClient car={car} />
      }
    } catch (e) {
      console.error("❌ [Server] Фоллбэк тоже не сработал:", e)
    }

    notFound()
  }
}
