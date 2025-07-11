import os
import aiohttp
import json
import logging
from datetime import datetime

class DiscordNotifier:
    def __init__(self):
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        if not self.webhook_url:
            logging.warning("Discord webhook URL não configurada")
    
    async def send_message(self, embed_data):
        """Envia mensagem para Discord"""
        if not self.webhook_url:
            logging.info("Discord não configurado, mensagem não enviada")
            return
            
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "embeds": [embed_data]
                }
                
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 204:
                        logging.info("Mensagem enviada para Discord com sucesso")
                    else:
                        logging.error(f"Erro ao enviar para Discord: {response.status}")
                        
        except Exception as e:
            logging.error(f"Erro ao enviar mensagem Discord: {e}")
    
    async def send_alert(self, host, results):
        """Envia alerta de problema"""
        embed = {
            "title": "🚨 ALERTA DE REDE",
            "description": f"Problemas detectados no host **{host['name']}**",
            "color": 0xff0000,  # Vermelho
            "fields": [
                {
                    "name": "Host",
                    "value": f"{host['name']} ({host['ip']})",
                    "inline": True
                },
                {
                    "name": "Perda de Pacotes",
                    "value": f"{results['packet_loss']:.1f}%",
                    "inline": True
                },
                {
                    "name": "Latência Média",
                    "value": f"{results['avg_latency']:.1f}ms",
                    "inline": True
                },
                {
                    "name": "Status",
                    "value": "🔴 Indisponível" if not results['is_available'] else "🟡 Degradado",
                    "inline": True
                }
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "Network Monitor"
            }
        }
        
        await self.send_message(embed)
    
    async def send_hourly_report(self, stats_data, chart_path=None):
        """Envia relatório consolidado"""
        embed = {
            "title": "📊 RELATÓRIO CONSOLIDADO",
            "description": "Resumo da última hora",
            "color": 0x00ff00,  # Verde
            "fields": [],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "Network Monitor - Relatório Automático"
            }
        }
        
        # Adicionar estatísticas de cada host
        for host_stats in stats_data:
            status_emoji = "🟢" if host_stats['availability'] >= 99 else "🟡" if host_stats['availability'] >= 95 else "🔴"
            
            embed["fields"].append({
                "name": f"{status_emoji} {host_stats['host_name']}",
                "value": f"**Disponibilidade:** {host_stats['availability']:.2f}%\n**Latência Média:** {host_stats['avg_latency']:.1f}ms\n**Perda de Pacotes:** {host_stats['packet_loss']:.1f}%",
                "inline": True
            })
        
        await self.send_message(embed)
        
        # Se houver gráfico, enviar em mensagem separada
        if chart_path and os.path.exists(chart_path):
            await self.send_chart(chart_path)
    
    async def send_error(self, host_name, error_message):
        """Envia notificação de erro"""
        embed = {
            "title": "⚠️ ERRO NO MONITORAMENTO",
            "description": f"Erro ao testar host **{host_name}**",
            "color": 0xffa500,  # Laranja
            "fields": [
                {
                    "name": "Erro",
                    "value": error_message,
                    "inline": False
                }
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "Network Monitor"
            }
        }
        
        await self.send_message(embed)
    
    async def send_chart(self, chart_path):
        """Envia gráfico como arquivo"""
        if not self.webhook_url:
            return
            
        try:
            async with aiohttp.ClientSession() as session:
                with open(chart_path, 'rb') as f:
                    form = aiohttp.FormData()
                    form.add_field('file', f, filename='network_stats.png')
                    
                    async with session.post(self.webhook_url, data=form) as response:
                        if response.status == 200:
                            logging.info("Gráfico enviado para Discord")
                        else:
                            logging.error(f"Erro ao enviar gráfico: {response.status}")
                            
        except Exception as e:
            logging.error(f"Erro ao enviar gráfico: {e}")
