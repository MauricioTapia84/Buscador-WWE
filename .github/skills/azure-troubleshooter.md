# 🛠 Azure FadeBooker Troubleshooter

Esta skill automatiza la recuperación del backend cuando Azure entra en estado "Blocked" o "Application Error".

## 📑 Comandos de Emergencia

### 1. Inyectar Credenciales ACR (Soluciona silent pull failures)
\`\`\`bash
ACR_PASS=$(az acr credential show --name fadebookerregistry --query "passwords[0].value" -o tsv)
az webapp config appsettings set --name fadebooker-backend-ok --resource-group FadeBooker --settings DOCKER_REGISTRY_SERVER_PASSWORD=$ACR_PASS
\`\`\`

### 2. Forzar Clean Start (Soluciona stuck containers)
\`\`\`bash
az webapp config set --name fadebooker-backend-ok --resource-group FadeBooker --startup-file "node src/index.js"
az webapp restart --name fadebooker-backend-ok --resource-group FadeBooker
\`\`\`

### 3. Log Streaming Express 5 (Diagnóstico de PathErrors)
\`\`\`bash
az webapp log tail --name fadebooker-backend-ok --resource-group FadeBooker | grep -E "Error|PathError|Module"
\`\`\`

## 🛡 Validaciones Críticas Linux
- Validar que \`ReporteController.js\` use \`generarReporteCitas\` (minúscula).
- Validar que \`app.js\` use \`(.*)\` en lugar de \`*\`.
- Validar integridad de \`infraestructure\` (sin 'u').
