# Network Monitor

Sistema completo de monitoramento de rede com Docker e Portainer Agent integrado.

## Instalação Rápida

```bash
git clone <seu-repositorio>
cd network-monitor
cp .env.example .env
# Configure o DISCORD_WEBHOOK_URL no arquivo .env
docker-compose up -d
