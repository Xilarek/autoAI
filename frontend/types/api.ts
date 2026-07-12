export type Verdict = "ЗВОНИТЬ" | "ТОРГОВАТЬСЯ" | "ДУМАТЬ" | "БЕЖАТЬ" | null

export interface ListingOut {
  id: number
  brand: string
  model: string
  year: number
  price: number
  mileage?: number
  region?: string
  market_price?: number
  verdict?: Verdict
  summary?: string
  risks?: string[]
  url?: string
  source?: "drom" | "avito" | "auto_ru"
  created_at?: string
}

export interface ReportsResponse {
  count: number
  total: number
  page: number
  per_page: number
  reports: ListingOut[]
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
