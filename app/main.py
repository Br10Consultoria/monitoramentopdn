#!/usr/bin/env python3
import asyncio
import json
import logging
import schedule
import time
from datetime import datetime, timedelta
import threading

from network_tests import NetworkTester
from discord_notifier import DiscordNotifier
from database import DatabaseManager
from stats_generator import StatsGenerator

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/data/network_monitor.log'),
        logging.StreamHandler()
    ]
)

class NetworkMonitor:
    def __init__(self):
        self.config = self.load_config()
        self.db = DatabaseManager()
        self.tester = NetworkTester(self.config)
        self.notifier = DiscordNotifier()
        self.stats = StatsGenerator(self.db)
        
    def load_config(self):
        try:
            with open('/app/config/hosts.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Erro ao carregar configuração: {e}")
            return {"hosts": [], "test_config": {}}

    async def run_network_tests(self):
        """Executa testes de rede para todos os hosts"""
        logging.info("Iniciando testes de rede...")
        
        for host in self.config['hosts']:
            try:
                logging.info(f"Testando host: {host['name']} ({host['ip']})")
                
                # Executar testes
                results = await self.tester.test_host(host)
                
                # Salvar no banco
                self.db.save_test_result(host, results)
                
                # Verificar se há problemas críticos
                if results['packet_loss'] > 10 or results['avg_latency'] > 1000:
                    await self.notifier.send_alert(host, results)
                    
            except Exception as e:
                logging.error(f"Erro ao testar host {host['name']}: {e}")
                await self.notifier.send_error(host['name'], str(e))

    async def generate_hourly_report(self):
        """Gera relatório consolidado a cada hora"""
        logging.info("Gerando relatório consolidado...")
        
        try:
            # Gerar estatísticas
            stats_data = self.stats.generate_hourly_stats()
            
            # Gerar gráficos
            chart_path = self.stats.generate_charts()
            
            # Enviar para Discord
            await self.notifier.send_hourly_report(stats_data, chart_path)
            
        except Exception as e:
            logging.error(f"Erro ao gerar relatório: {e}")

    def schedule_tasks(self):
        """Agenda as tarefas"""
        test_interval = self.config['test_config'].get('test_interval_minutes', 5)
        
        # Testes a cada X minutos
        schedule.every(test_interval).minutes.do(
            lambda: asyncio.run(self.run_network_tests())
        )
        
        # Relatório a cada hora
        schedule.every().hour.do(
            lambda: asyncio.run(self.generate_hourly_report())
        )

    def run(self):
        """Executa o monitor"""
        logging.info("Iniciando Network Monitor...")
        
        # Executar teste inicial
        asyncio.run(self.run_network_tests())
        
        # Agendar tarefas
        self.schedule_tasks()
        
        # Loop principal
        while True:
            schedule.run_pending()
            time.sleep(30)

if __name__ == "__main__":
    monitor = NetworkMonitor()
    monitor.run()
