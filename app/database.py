import sqlite3
import json
import logging
from datetime import datetime, timedelta
import threading

class DatabaseManager:
    def __init__(self, db_path='/app/data/network_monitor.db'):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabela de resultados de testes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    host_name TEXT,
                    host_ip TEXT,
                    packet_loss REAL,
                    avg_latency REAL,
                    min_latency REAL,
                    max_latency REAL,
                    jitter REAL,
                    is_available BOOLEAN,
                    successful_pings INTEGER,
                    total_pings INTEGER,
                    traceroute TEXT
                )
            ''')
            
            # Índices para performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON test_results(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_host_name ON test_results(host_name)')
            
            conn.commit()
            conn.close()
    
    def save_test_result(self, host, results):
        """Salva resultado de teste no banco"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO test_results 
                    (timestamp, host_name, host_ip, packet_loss, avg_latency, 
                     min_latency, max_latency, jitter, is_available, 
                     successful_pings, total_pings, traceroute)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    results['timestamp'],
                    host['name'],
                    host['ip'],
                    results['packet_loss'],
                    results['avg_latency'],
                    results['min_latency'],
                    results['max_latency'],
                    results['jitter'],
                    results['is_available'],
                    results['successful_pings'],
                    results['total_pings'],
                    json.dumps(results['traceroute'])
                ))
                
                conn.commit()
                conn.close()
                
            except Exception as e:
                logging.error(f"Erro ao salvar resultado: {e}")
    
    def get_hourly_stats(self, hours_back=1):
        """Obtém estatísticas da última(s) hora(s)"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cutoff_time = (datetime.now() - timedelta(hours=hours_back)).timestamp()
                
                cursor.execute('''
                    SELECT host_name, host_ip,
                           AVG(packet_loss) as avg_packet_loss,
                           AVG(avg_latency) as avg_latency,
                           MIN(min_latency) as min_latency,
                           MAX(max_latency) as max_latency,
                           AVG(jitter) as avg_jitter,
                           SUM(CASE WHEN is_available THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as availability,
                           COUNT(*) as total_tests
                    FROM test_results 
                    WHERE timestamp > ?
                    GROUP BY host_name, host_ip
                ''', (cutoff_time,))
                
                results = cursor.fetchall()
                conn.close()
                
                return [{
                    'host_name': row[0],
                    'host_ip': row[1],
                    'packet_loss': row[2] or 0,
                    'avg_latency': row[3] or 0,
                    'min_latency': row[4] or 0,
                    'max_latency': row[5] or 0,
                    'jitter': row[6] or 0,
                    'availability': row[7] or 0,
                    'total_tests': row[8] or 0
                } for row in results]
                
            except Exception as e:
                logging.error(f"Erro ao obter estatísticas: {e}")
                return []
    
    def get_historical_data(self, host_name, hours_back=24):
        """Obtém dados históricos de um host"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cutoff_time = (datetime.now() - timedelta(hours=hours_back)).timestamp()
                
                cursor.execute('''
                    SELECT timestamp, avg_latency, packet_loss, is_available
                    FROM test_results 
                    WHERE host_name = ? AND timestamp > ?
                    ORDER BY timestamp
                ''', (host_name, cutoff_time))
                
                results = cursor.fetchall()
                conn.close()
                
                return results
                
            except Exception as e:
                logging.error(f"Erro ao obter dados históricos: {e}")
                return []
    
    def cleanup_old_data(self, days_to_keep=30):
        """Remove dados antigos"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cutoff_time = (datetime.now() - timedelta(days=days_to_keep)).timestamp()
                
                cursor.execute('DELETE FROM test_results WHERE timestamp < ?', (cutoff_time,))
                
                deleted_rows = cursor.rowcount
                conn.commit()
                conn.close()
                
                logging.info(f"Removidos {deleted_rows} registros antigos")
                
            except Exception as e:
                logging.error(f"Erro na limpeza de dados: {e}")
