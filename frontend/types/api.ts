export type Verdict = "ЗВОНИТЬ" | "ТОРГОВАТЬСЯ" | "ДУМАТЬ" | "БЕЖАТЬ" | null

export interface ListingOut {
  id: number
  brand: string
  model: string
  year: number
  price_rub: number // Было price
  fair_price?: number // Было market_price
  mileage?: number
  region?: string
  ai_verdict?: Verdict // Было verdict
  ai_summary?: string // Было summary
  ai_risks?: string[] // Было risks
  url?: string
  source?: "drom" | "avito" | "auto_ru" | string
  photos?: string[]
  created_at?: string
  description?: string
  engine_volume?: number
  fuel_type?: string
  transmission?: string
  body_type?: string
}

// Если бэкенд возвращает просто массив, используем его.
// Если позже добавят пагинацию в виде объекта, мы это адаптируем.
export type ReportsResponse =
  ListingOut[] | { reports: ListingOut[]; total: number; per_page: number }

export interface ReportsParams {
  skip?: number
  limit?: number
  verdict?: string
  brand?: string
  model?: string
  region?: string
  sort_by?: "price_rub" | "year" | "created_at"
  sort_order?: "asc" | "desc"
}

export interface ParseResponse {
  status: "queued" | "running" | "completed" | "failed"
  task_id: string
  platform: string
  message: string
}

export interface TaskStatus {
  task_id: string
  status: "PENDING" | "STARTED" | "SUCCESS" | "FAILURE" | "RETRY"
  result?: { status: string; count: number; platform: string }
  listings?: ListingOut[]
  error?: string
}

export interface SearchParams {
  query?: string
  region?: string
  price_min?: number | null
  price_max?: number | null
  year_min?: number | null
  year_max?: number | null
  brand?: string | null
  model?: string | null
}
