import { apiClient } from "./client"
import type { SearchParams, ParseResponse, TaskStatus } from "@/types/api"

export const parsersApi = {
  getPlatforms: () => 
    apiClient.get<{ platforms: string[]; count: number }>("/parsers/platforms"),
  
  startParsing: (platform: string, params: SearchParams) =>
    apiClient.post<ParseResponse>(`/parsers/${platform}/search`, params),
  
  getTaskStatus: (taskId: string) =>
    apiClient.get<TaskStatus>(`/parsers/tasks/${taskId}`),
}
