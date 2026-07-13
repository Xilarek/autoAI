import axios from "axios"

// На сервере (Node.js) нужен абсолютный URL. На клиенте (браузер) можно использовать относительный.
const isServer = typeof window === "undefined"
const apiBaseUrl = isServer
  ? `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1`
  : "/api/v1"

export const apiClient = axios.create({
  baseURL: apiBaseUrl,
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Теперь используем только console, это безопасно для Server Components
    if (error.code === "ECONNABORTED") {
      console.error("⏱️ Превышено время ожидания ответа от сервера")
    } else if (error.response) {
      console.error(
        `❌ Ошибка API: ${error.response.status} - ${error.response.data?.detail || "Неизвестная ошибка"}`
      )
    } else {
      console.error(`🌐 Ошибка сети. URL запроса: ${error.config?.url}`)
    }
    return Promise.reject(error)
  }
)
