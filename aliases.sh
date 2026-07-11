#!/bin/bash

# Быстрые команды для AutoAI
alias ai-start='cd /c/autoAI/auto-ai && ./start.sh start'
alias ai-stop='cd /c/autoAI/auto-ai && ./start.sh stop'
alias ai-restart='cd /c/autoAI/auto-ai && ./start.sh restart'
alias ai-status='cd /c/autoAI/auto-ai && ./start.sh status'
alias ai-logs='cd /c/autoAI/auto-ai && ./start.sh logs'
alias ai-ai='cd /c/autoAI/auto-ai && ./start.sh ai'
alias ai-parse='cd /c/autoAI/auto-ai && ./start.sh parse'

echo "✅ Алиасы загружены. Используйте:"
echo "   ai-start   - запустить проект"
echo "   ai-stop    - остановить проект"
echo "   ai-restart - перезапустить проект"
echo "   ai-status  - показать статус"
echo "   ai-logs    - показать логи"
echo "   ai-ai      - запустить AI-анализ"
echo "   ai-parse   - запустить парсинг"
