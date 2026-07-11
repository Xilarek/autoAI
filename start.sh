#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода заголовка
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  🚗 AutoAI - Система подбора авто${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# Функция для проверки Docker
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker Desktop не запущен!${NC}"
        echo -e "${YELLOW}💡 Запустите Docker Desktop и попробуйте снова.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker работает${NC}"
}

# Функция для запуска проекта
start_project() {
    print_header
    echo -e "${BLUE}[*] Проверка Docker...${NC}"
    check_docker
    
    echo -e "${BLUE}[*] Запуск контейнеров...${NC}"
    docker-compose up -d
    
    echo ""
    echo -e "${BLUE}[*] Ожидание запуска сервисов (10 сек)...${NC}"
    sleep 10
    
    echo ""
    echo -e "${BLUE}[*] Статус контейнеров:${NC}"
    docker-compose ps
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  ✅ Проект запущен!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}📊 Swagger UI:${NC} http://localhost:8000/docs"
    echo -e "${YELLOW}🎨 Frontend:${NC} http://localhost:3000 (если запущен)"
    echo ""
}

# Функция для остановки проекта
stop_project() {
    print_header
    echo -e "${BLUE}[*] Остановка контейнеров...${NC}"
    docker-compose down
    
    echo ""
    echo -e "${GREEN}✅ Проект остановлен${NC}"
}

# Функция для перезапуска проекта
restart_project() {
    print_header
    echo -e "${BLUE}[*] Перезапуск контейнеров...${NC}"
    docker-compose restart
    
    echo ""
    echo -e "${BLUE}[*] Ожидание запуска (10 сек)...${NC}"
    sleep 10
    
    echo ""
    echo -e "${BLUE}[*] Статус контейнеров:${NC}"
    docker-compose ps
    
    echo ""
    echo -e "${GREEN}✅ Проект перезапущен${NC}"
}

# Функция для просмотра логов
show_logs() {
    print_header
    echo -e "${BLUE}[*] Логи контейнеров (Ctrl+C для выхода):${NC}"
    echo ""
    docker-compose logs -f
}

# Функция для проверки статуса
show_status() {
    print_header
    echo -e "${BLUE}[*] Статус контейнеров:${NC}"
    echo ""
    docker-compose ps
    
    echo ""
    echo -e "${BLUE}[*] Использование ресурсов:${NC}"
    docker stats --no-stream
}

# Функция для запуска AI-анализа
run_ai_analysis() {
    print_header
    echo -e "${BLUE}[*] Запуск AI-анализа всех объявлений...${NC}"
    echo ""
    
    # Вызываем API endpoint
    curl -X POST "http://localhost:8000/api/v1/ai/analyze-all" \
         -H "accept: application/json" \
         -H "Content-Type: application/json" \
         -d '{}' > /dev/null
    
    echo -e "${GREEN}✅ AI-анализ запущен в фоне${NC}"
    echo -e "${YELLOW}💡 Подождите 10-15 секунд, затем проверьте результаты:${NC}"
    echo -e "   http://localhost:8000/docs → GET /api/v1/ai/reports"
    echo ""
}

# Функция для парсинга Дрома
parse_drom() {
    print_header
    echo -e "${BLUE}[*] Запуск парсинга Дрома...${NC}"
    echo ""
    
    # Вызываем API endpoint
    curl -X POST "http://localhost:8000/api/v1/parsers/drom/search" \
         -H "accept: application/json" \
         -H "Content-Type: application/json" \
         -d '{"query": "", "region": ""}' > /dev/null
    
    echo -e "${GREEN}✅ Парсинг завершён${NC}"
    echo -e "${YELLOW}💡 Проверьте результаты:${NC}"
    echo -e "   http://localhost:8000/docs → GET /api/v1/cars/"
    echo ""
}

# Главное меню
show_menu() {
    echo ""
    echo -e "${BLUE}Выберите действие:${NC}"
    echo "  1) 🚀 Запустить проект"
    echo "  2) 🛑 Остановить проект"
    echo "  3) 🔄 Перезапустить проект"
    echo "  4) 📊 Показать статус"
    echo "  5) 📋 Показать логи"
    echo "  6) 🤖 Запустить AI-анализ"
    echo "  7) 🕷️ Запустить парсинг Дрома"
    echo "  0) ❌ Выход"
    echo ""
    read -p "Введите номер: " choice
    
    case $choice in
        1) start_project ;;
        2) stop_project ;;
        3) restart_project ;;
        4) show_status ;;
        5) show_logs ;;
        6) run_ai_analysis ;;
        7) parse_drom ;;
        0) exit 0 ;;
        *) echo -e "${RED}❌ Неверный выбор${NC}" ;;
    esac
}

# Обработка аргументов командной строки
if [ $# -eq 0 ]; then
    # Интерактивный режим
    while true; do
        show_menu
    done
else
    # Режим командной строки
    case "$1" in
        start) start_project ;;
        stop) stop_project ;;
        restart) restart_project ;;
        status) show_status ;;
        logs) show_logs ;;
        ai) run_ai_analysis ;;
        parse) parse_drom ;;
        *) 
            echo "Использование: $0 {start|stop|restart|status|logs|ai|parse}"
            exit 1
            ;;
    esac
fi
