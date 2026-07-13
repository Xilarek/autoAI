import { apiClient } from "./client"
import type { ReportsResponse, ReportsParams, ListingOut } from "@/types/api"

export const carsApi = {
  getList: (params?: ReportsParams) =>
    apiClient.get<ReportsResponse>("/cars", { params }),

  getById: (id: number) =>
    apiClient.get<ListingOut>(`/cars/${id}`),
}
