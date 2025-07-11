#!/bin/bash
# setup-portainer.sh

echo "🔧 Configurando Portainer Agent para conexão com nuvem..."

# Verificar se as variáveis necessárias estão definidas
if [ -z "$AGENT_SECRET" ]; then
    echo "⚠️  AGENT_SECRET não definido no .env"
    echo "Você pode obter este valor no seu Portainer na nuvem em:"
    echo "Environments > Add Environment > Agent"
    echo ""
fi

# Mostrar informações de configuração
echo "📋 Configuração atual:"
echo "AGENT_PORT: ${AGENT_PORT:-9001}"
echo "AGENT_CLUSTER_ADDR: ${AGENT_CLUSTER_ADDR:-network-monitor-agent}"
echo "PORTAINER_ENVIRONMENT_NAME: ${PORTAINER_ENVIRONMENT_NAME:-production}"
echo ""

# Verificar se o agent está rodando
if docker-compose ps portainer-agent | grep -q "Up"; then
    echo "✅ Portainer Agent está rodando"
    echo "🌐 Agent acessível em: $(hostname -I | awk '{print $1}'):${AGENT_PORT:-9001}"
    echo ""
    echo "📝 Para adicionar este environment no Portainer:"
    echo "1. Acesse seu Portainer na nuvem"
    echo "2. Vá em 'Environments'"
    echo "3. Clique em 'Add environment'"
    echo "4. Selecione 'Agent'"
    echo "5. Use as informações:"
    echo "   - Name: ${PORTAINER_ENVIRONMENT_NAME:-network-monitor-server}"
    echo "   - Environment URL: $(hostname -I | awk '{print $1}'):${AGENT_PORT:-9001}"
    if [ ! -z "$AGENT_SECRET" ]; then
        echo "   - Agent secret: ${AGENT_SECRET}"
    fi
else
    echo "❌ Portainer Agent não está rodando"
    echo "Execute: docker-compose up -d portainer-agent"
fi
