$env:N8N_PORT="5678"
$env:N8N_HOST="localhost"
$env:N8N_DIAGNOSTICS_ENABLED="false"
$env:N8N_PERSONALIZATION_ENABLED="false"
$env:EXECUTIONS_DATA_SAVE_ON_ERROR="all"
$env:EXECUTIONS_DATA_SAVE_ON_SUCCESS="none"
$env:EXECUTIONS_DATA_SAVE_ON_PROGRESS="false"

Write-Host "🚀 Starting Customized n8n for MiroFish OS..."
npx n8n
