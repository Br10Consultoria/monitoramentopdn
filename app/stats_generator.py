import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging
import os

class StatsGenerator:
    def __init__(self, db_manager):
        self.db = db_manager
        
    def generate_hourly_stats(self):
        """Gera estatísticas da última hora"""
        return self.db.get_hourly_stats(1)
    
    def generate_charts(self):
        """Gera gráficos de monitoramento"""
        try:
            # Obter dados de todos os hosts das últimas 24 horas
            stats = self.db.get_hourly_stats(24)
            
            if not stats:
                logging.warning("Sem dados para gerar gráficos")
                return None
            
            # Criar figura com subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Network Monitor - Últimas 24 Horas', fontsize=16)
            
            hosts = [stat['host_name'] for stat in stats]
            
            # Gráfico 1: Disponibilidade
            availability = [stat['availability'] for stat in stats]
            bars1 = ax1.bar(hosts, availability, color=['green' if a >= 99 else 'orange' if a >= 95 else 'red' for a in availability])
            ax1.set_title('Disponibilidade por Host (%)')
            ax1.set_ylabel('Disponibilidade (%)')
            ax1.set_ylim(0, 100)
            ax1.tick_params(axis='x', rotation=45)
            
            # Adicionar valores nas barras
            for bar, value in zip(bars1, availability):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                        f'{value:.1f}%', ha='center', va='bottom')
            
            # Gráfico 2: Latência Média
            latencies = [stat['avg_latency'] for stat in stats]
            bars2 = ax2.bar(hosts, latencies, color='blue', alpha=0.7)
            ax2.set_title('Latência Média por Host (ms)')
            ax2.set_ylabel('Latência (ms)')
            ax2.tick_params(axis='x', rotation=45)
            
            # Gráfico 3: Perda de Pacotes
            packet_loss = [stat['packet_loss'] for stat in stats]
            bars3 = ax3.bar(hosts, packet_loss, color='red', alpha=0.7)
            ax3.set_title('Perda de Pacotes por Host (%)')
            ax3.set_ylabel('Perda de Pacotes (%)')
            ax3.tick_params(axis='x', rotation=45)
            
            # Gráfico 4: Jitter
            jitter = [stat['jitter'] for stat in stats]
            bars4 = ax4.bar(hosts, jitter, color='purple', alpha=0.7)
            ax4.set_title('Jitter por Host (ms)')
            ax4.set_ylabel('Jitter (ms)')
            ax4.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            # Salvar gráfico
            chart_path = '/app/reports/network_stats.png'
            os.makedirs(os.path.dirname(chart_path), exist_ok=True)
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logging.info(f"Gráfico salvo em: {chart_path}")
            return chart_path
            
        except Exception as e:
            logging.error(f"Erro ao gerar gráficos: {e}")
            return None
    
    def generate_interactive_dashboard(self):
        """Gera dashboard interativo com Plotly"""
        try:
            stats = self.db.get_hourly_stats(24)
            
            if not stats:
                return None
            
            df = pd.DataFrame(stats)
            
            # Criar dashboard interativo
            fig = go.Figure()
            
            # Gráfico de disponibilidade
            fig.add_trace(go.Bar(
                name='Disponibilidade',
                x=df['host_name'],
                y=df['availability'],
                yaxis='y',
                marker_color='green'
            ))
            
            # Gráfico de latência
            fig.add_trace(go.Scatter(
                name='Latência Média',
                x=df['host_name'],
                y=df['avg_latency'],
                yaxis='y2',
                mode='lines+markers',
                marker_color='blue'
            ))
            
            # Layout
            fig.update_layout(
                title='Network Monitor Dashboard',
                xaxis=dict(domain=[0, 1]),
                yaxis=dict(
                    title='Disponibilidade (%)',
                    side='left'
                ),
                yaxis2=dict(
                    title='Latência (ms)',
                    side='right',
                    overlaying='y'
                ),
                height=600
            )
            
            # Salvar dashboard
            dashboard_path = '/app/reports/dashboard.html'
            fig.write_html(dashboard_path)
            
            return dashboard_path
            
        except Exception as e:
            logging.error(f"Erro ao gerar dashboard: {e}")
            return None
    
    def calculate_sla(self, host_name, period_days=30):
        """Calcula SLA de um host"""
        try:
            historical_data = self.db.get_historical_data(host_name, period_days * 24)
            
            if not historical_data:
                return 0
            
            total_tests = len(historical_data)
            successful_tests = sum(1 for data in historical_data if data[3])  # is_available
            
            sla = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
            
            return sla
            
        except Exception as e:
            logging.error(f"Erro ao calcular SLA: {e}")
            return 0
