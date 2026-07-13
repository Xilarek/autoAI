export const VERDICT_CONFIG: Record<
  string,
  { label: string; color: string; bg: string; icon: string }
> = {
  ЗВОНИТЬ: { label: "ЗВОНИТЬ", color: "text-green-600", bg: "bg-green-100", icon: "Phone" },
  ТОРГОВАТЬСЯ: {
    label: "ТОРГОВАТЬСЯ",
    color: "text-blue-600",
    bg: "bg-blue-100",
    icon: "MessageCircle",
  },
  ДУМАТЬ: { label: "ДУМАТЬ", color: "text-yellow-600", bg: "bg-yellow-100", icon: "Brain" },
  БЕЖАТЬ: { label: "БЕЖАТЬ", color: "text-red-600", bg: "bg-red-100", icon: "AlertTriangle" },
}

export const PLATFORMS = {
  drom: { name: "Дром", color: "bg-blue-600" },
  avito: { name: "Авито", color: "bg-green-600" },
  auto_ru: { name: "Auto.ru", color: "bg-red-600" },
} as const

export const REGIONS = [
  { value: "moscow", label: "Москва" },
  { value: "spb", label: "Санкт-Петербург" },
  { value: "novosibirsk", label: "Новосибирск" },
  { value: "ekaterinburg", label: "Екатеринбург" },
  { value: "kazan", label: "Казань" },
] as const
