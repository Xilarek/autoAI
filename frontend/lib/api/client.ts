import axios from "axios"

export const apiClient = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === "ECONNABORTED") {
      console.error("⏱️ Превышено время ожидания ответа от сервера")
    } else if (error.response) {
      console.error(`❌ Ошибка API: ${error.response.status}`)
    } else {
      console.error("🌐 Ошибка сети")
    }
    return Promise.reject(error)
  }
)
