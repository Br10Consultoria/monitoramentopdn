import asyncio
import subprocess
import statistics
import time
from pythonping import ping
import logging

class NetworkTester:
    def __init__(self, config):
        self.config = config
        
    async def test_host(self, host):
        """Executa todos os testes para um host"""
        results = {
            'timestamp': time.time(),
            'host_name': host['name'],
            'host_ip': host['ip'],
            'ping_results': {},
            'traceroute': [],
            'packet_loss': 0,
            'avg_latency': 0,
            'min_latency': 0,
            'max_latency': 0,
            'jitter': 0,
            'is_available': False
        }
        
        # Teste de ping
        ping_results = await self.run_ping_test(host['ip'])
        results.update(ping_results)
        
        # Traceroute (apenas se o host estiver disponível)
        if results['is_available']:
            traceroute_results = await self.run_traceroute(host['ip'])
            results['traceroute'] = traceroute_results
            
        return results
    
    async def run_ping_test(self, host_ip):
        """Executa teste de ping"""
        ping_count = self.config['test_config'].get('ping_count', 50)
        timeout = self.config['test_config'].get('timeout', 5)
        
        try:
            # Executar pings
            response_times = []
            successful_pings = 0
            
            for i in range(ping_count):
                try:
                    response = ping(host_ip, timeout=timeout, count=1)
                    if response.success():
                        response_times.append(response.rtt_avg_ms)
                        successful_pings += 1
                except:
                    pass
                    
                # Pequena pausa entre pings
                await asyncio.sleep(0.1)
            
            # Calcular estatísticas
            packet_loss = ((ping_count - successful_pings) / ping_count) * 100
            
            if response_times:
                avg_latency = statistics.mean(response_times)
                min_latency = min(response_times)
                max_latency = max(response_times)
                jitter = statistics.stdev(response_times) if len(response_times) > 1 else 0
                is_available = True
            else:
                avg_latency = min_latency = max_latency = jitter = 0
                is_available = False
            
            return {
                'packet_loss': packet_loss,
                'avg_latency': avg_latency,
                'min_latency': min_latency,
                'max_latency': max_latency,
                'jitter': jitter,
                'is_available': is_available,
                'successful_pings': successful_pings,
                'total_pings': ping_count
            }
            
        except Exception as e:
            logging.error(f"Erro no teste de ping para {host_ip}: {e}")
            return {
                'packet_loss': 100,
                'avg_latency': 0,
                'min_latency': 0,
                'max_latency': 0,
                'jitter': 0,
                'is_available': False,
                'successful_pings': 0,
                'total_pings': ping_count
            }
    
    async def run_traceroute(self, host_ip):
        """Executa traceroute"""
        try:
            process = await asyncio.create_subprocess_exec(
                'traceroute', '-n', '-w', '3', host_ip,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return stdout.decode().strip().split('\n')
            else:
                return [f"Erro no traceroute: {stderr.decode()}"]
                
        except Exception as e:
            logging.error(f"Erro no traceroute para {host_ip}: {e}")
            return [f"Erro no traceroute: {str(e)}"]
