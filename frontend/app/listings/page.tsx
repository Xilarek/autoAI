import ListingsClient from "./ListingsClient"
import type { Metadata } from "next"

// Метаданные теперь здесь, так как это Server Component (без "use client")
export const metadata: Metadata = {
  title: "Каталог автомобилей",
  description:
    "Просмотрите проверенные AI объявления автомобилей. Фильтры, сортировка и умные рекомендации.",
}

export default function ListingsPage() {
  return <ListingsClient />
}
