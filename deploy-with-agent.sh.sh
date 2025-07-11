#!/bin/bash
# deploy-with-agent.sh

echo "🚀 Iniciando deploy do Network Monitor + Portainer Agent..."

# Criar diretórios necessários
mkdir -p config data reports

# Verificar se o .env existe
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "Criando template do .env..."
    cat > .env << EOF
# Discord Configuration
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_url_here
EOF
    echo "📝 Configure o arquivo .env antes de continuar"
    exit 1
fi

# Carregar variáveis do .env
source .env

# Verificar configuração do Discord
if [ "$DISCORD_WEBHOOK_URL" = "https://discord.com/api/webhooks/your_webhook_url_here" ]; then
    echo "⚠️  Configure o DISCORD_WEBHOOK_URL no arquivo .env"
    exit 1
fi

echo "1️⃣ Iniciando Portainer Agent..."
# Parar e remover container existente se houver
docker stop portainer_agent 2>/dev/null || true
docker rm portainer_agent 2>/dev/null || true

# Executar o comando específico do Portainer Agent
docker run -d \
  -p 9001:9001 \
  --name portainer_agent \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /var/lib/docker/volumes:/var/lib/docker/volumes \
  -v /:/host \
  portainer/agent:2.27.8

echo "2️⃣ Construindo e iniciando Network Monitor..."
# Build e start do network monitor
docker-compose build
docker-compose up -d

# Aguardar containers iniciarem
echo "⏳ Aguardando containers iniciarem..."
sleep 10

# Verificar status
echo ""
echo "✅ Status dos serviços:"

if docker ps | grep -q "portainer_agent"; then
    echo "  - Portainer Agent: ✅ Rodando"
else
    echo "  - Portainer Agent: ❌ Erro"
fi

if docker-compose ps network-monitor | grep -q "Up"; then
    echo "  - Network Monitor: ✅ Rodando"
else
    echo "  - Network Monitor: ❌ Erro"
fi

echo ""
echo "📊 Informações de acesso:"
echo "🌐 Portainer Agent: $(hostname -I | awk '{print $1}'):9001"

# Tentar obter IP público
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null)
if [ ! -z "$PUBLIC_IP" ]; then
    echo "🌍 IP Público: ${PUBLIC_IP}:9001"
fi

echo ""
echo "📁 Arquivos importantes:"
echo "  - Logs: ./data/network_monitor.log"
echo "  - Config: ./config/hosts.json"
echo "  - Dados: ./data/network_monitor.db"

echo ""
echo "🔧 Comandos úteis:"
echo "  - Ver logs monitor: docker-compose logs -f network-monitor"
echo "  - Ver logs agent: docker logs portainer_agent -f"
echo "  - Parar tudo: docker-compose down && docker stop portainer_agent"
echo "  - Reiniciar monitor: docker-compose restart"
echo "  - Reiniciar agent: docker restart portainer_agent"

echo ""
echo "🌐 Para conectar ao Portainer na nuvem:"
echo "  1. Acesse seu Portainer"
echo "  2. Environments > Add Environment > Agent"
echo "  3. Environment URL: $(hostname -I | awk '{print $1}'):9001"
echo "  4. Nome: network-monitor-server"
