import axios from "axios"
import type { SearchParams, ParseResponse, TaskStatus, ReportsResponse, ReportsParams } from "@/types/api"

const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
})

export const parsersApi = {
  getPlatforms: () => api.get<{ platforms: string[]; count: number }>("/parsers/platforms"),
  startParsing: (platform: string, params: SearchParams) =>
    api.post<ParseResponse>(`/parsers/${platform}/search`, params),
  getTaskStatus: (taskId: string) =>
    api.get<TaskStatus>(`/parsers/tasks/${taskId}`),
}

export const aiApi = {
  getReports: (params?: ReportsParams) =>
    api.get<ReportsResponse>("/ai/reports", { params }),
  getReport: (id: number) =>
    api.get(`/ai/report/${id}`),
  analyzeAll: () => api.post("/ai/analyze-all"),
}

export const carsApi = {
  getList: (params?: ReportsParams) =>
    api.get<ReportsResponse>("/cars", { params }),
}
