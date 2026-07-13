import axios from "axios"
import { toast } from "sonner"

export const apiClient = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const message = error.response.data?.detail || "Произошла ошибка сервера"
      toast.error(message)
    } else {
      toast.error("Ошибка сети. Проверьте интернет.")
    }
    return Promise.reject(error)
  }
)
