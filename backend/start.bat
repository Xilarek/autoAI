@echo off
cd /d C:\autoAI\auto-ai
echo Запускаю AutoAI...
docker-compose up -d
echo.
echo Статус контейнеров:
docker-compose ps
echo.
echo Swagger UI: http://localhost:8000/docs
pause