from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import sqlite3
import time
import json
import sys
import threading

class HFTVulnerableSQLiServer(BaseHTTPRequestHandler):
    
    SECRET_PASSWORD = "TraderPass123!"
    
    # Глобальные структуры для имитации HFT окружения
    _market_data_cache = {}
    _cache_lock = threading.Lock()
    _trading_volume = 0
    
    def init_db(self):
        """Инициализация БД для HFT"""
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE traders (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT,
                api_key TEXT,
                balance REAL,
                trades_count INTEGER,
                last_trade TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE market_orders (
                id INTEGER PRIMARY KEY,
                trader_id INTEGER,
                symbol TEXT,
                side TEXT,
                price REAL,
                quantity INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Данные для HFT
        traders = [
            (1, 'admin', self.SECRET_PASSWORD, 'API-KEY-ADMIN-123', 1000000.0, 1500, time.time()),
            (2, 'trader1', 'Pass123!', 'API-KEY-TRADER-456', 500000.0, 800, time.time()),
            (3, 'trader2', 'SecurePass!', 'API-KEY-TRADER-789', 750000.0, 1200, time.time())
        ]
        
        cursor.executemany('INSERT INTO traders VALUES (?,?,?,?,?,?,?)', traders)
        conn.commit()
        return conn
    
    def execute_conditional_query(self, condition):
        """
        УЯЗВИМЫЙ метод для HFT
        Использует SLEEP/BENCHMARK для демонстрации timing атак
        """
        conn = self.init_db()
        cursor = conn.cursor()
        
        start_time = time.perf_counter()
        
        try:
            # УЯЗВИМЫЙ КОД - прямое выполнение SQL
            query = f"SELECT COUNT(*) FROM traders WHERE {condition}"
            cursor.execute(query)
            result = cursor.fetchone()[0]
            
            # Timing-based уязвимость для HFT
            if result > 0:
                # Используем разные методы задержки для демонстрации
                if "SLEEP" in condition.upper():
                    # Извлекаем параметр SLEEP
                    import re
                    sleep_match = re.search(r'SLEEP\s*\(\s*(\d+\.?\d*)\s*\)', condition, re.IGNORECASE)
                    if sleep_match:
                        sleep_time = float(sleep_match.group(1))
                        time.sleep(sleep_time)
                elif "BENCHMARK" in condition.upper():
                    # Эмулируем BENCHMARK нагрузку
                    benchmark_match = re.search(r'BENCHMARK\s*\(\s*(\d+)\s*,\s*', condition, re.IGNORECASE)
                    if benchmark_match:
                        iterations = int(benchmark_match.group(1))
                        # Имитация нагрузки
                        for _ in range(min(iterations, 10000)):
                            _ = hashlib.md5(str(time.time()).encode()).hexdigest()
                else:
                    # Стандартная задержка для HFT (1 мс)
                    time.sleep(0.001)
            
            elapsed = time.perf_counter() - start_time
            
            return {
                'success': True,
                'time': elapsed,
                'result': result,
                'condition_was_true': result > 0,
                'query': query
            }
            
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            return {
                'success': False,
                'time': elapsed,
                'error': str(e),
                'query': query if 'query' in locals() else 'Unknown'
            }
        finally:
            conn.close()
    
    def check_market_condition(self, condition):
        """
        Метод для проверки рыночных условий с timing уязвимостью
        Используется в HFT для принятия торговых решений
        """
        conn = self.init_db()
        cursor = conn.cursor()
        
        start_time = time.perf_counter()
        
        try:
            # Уязвимость в HFT логике
            query = f"""
                SELECT COUNT(*) FROM market_orders mo
                JOIN traders t ON mo.trader_id = t.id
                WHERE {condition}
                AND mo.timestamp > datetime('now', '-1 minute')
            """
            cursor.execute(query)
            result = cursor.fetchone()[0]
            
            # Задержка при выполнении условия
            if result > 0:
                time.sleep(0.001)  # 1 мс задержка
            
            elapsed = time.perf_counter() - start_time
            
            return {
                'market_condition': condition,
                'orders_found': result,
                'execution_time_ms': elapsed * 1000,
                'has_delay': result > 0
            }
            
        except Exception as e:
            return {'error': str(e)}
        finally:
            conn.close()
    
    def do_GET(self):
        """Обработка GET запросов для HFT"""
        parsed = urlparse(self.path)
        
        if parsed.path == '/info':
            self.send_json({
                'server': 'HFT УЯЗВИМЫЙ Timing SQL Injection Server',
                'purpose': 'Демонстрация timing атак в высокочастотной торговле',
                'password': self.SECRET_PASSWORD,
                'vulnerabilities': [
                    'Time-based SQL Injection',
                    'Blind SQL Injection',
                    'SLEEP/BENCHMARK атаки',
                    'Подбор параметров торгов'
                ],
                'hft_features': [
                    'Микросекундные задержки',
                    'Рыночные данные в реальном времени',
                    'Торговые условия с timing'
                ]
            })
        
        elif parsed.path == '/check':
            """Основной endpoint для timing атак в HFT"""
            params = parse_qs(parsed.query)
            condition = params.get('condition', [''])[0]
            
            if condition:
                result = self.execute_conditional_query(condition)
                self.send_json(result)
            else:
                self.send_error(400, 'No condition provided')
        
        elif parsed.path == '/market':
            """Endpoint для проверки рыночных условий"""
            params = parse_qs(parsed.query)
            condition = params.get('condition', [''])[0]
            
            if condition:
                # Уязвимость: пользовательский ввод в SQL
                result = self.check_market_condition(condition)
                self.send_json(result)
            else:
                self.send_json({
                    'market_orders': 150,
                    'active_traders': 42,
                    'avg_execution_time_ms': 0.5
                })
        
        elif parsed.path == '/trade':
            """Уязвимый endpoint для выполнения trades"""
            params = parse_qs(parsed.query)
            api_key = params.get('api_key', [''])[0]
            symbol = params.get('symbol', [''])[0]
            side = params.get('side', [''])[0]
            quantity = params.get('quantity', ['0'])[0]
            
            # УЯЗВИМЫЙ КОД для HFT
            query = f"""
                SELECT * FROM traders 
                WHERE api_key = '{api_key}'
                AND username IN (SELECT username FROM traders WHERE balance > 0)
            """
            
            conn = self.init_db()
            cursor = conn.cursor()
            
            try:
                cursor.execute(query)
                trader = cursor.fetchone()
                
                if trader:
                    # Timing уязвимость: задержка при успешной авторизации
                    time.sleep(0.001)
                    
                    with self._cache_lock:
                        self._trading_volume += int(quantity)
                    
                    self.send_json({
                        'trade_executed': True,
                        'trader_id': trader[0],
                        'symbol': symbol,
                        'side': side,
                        'quantity': quantity,
                        'timestamp': time.time(),
                        'total_volume': self._trading_volume
                    })
                else:
                    self.send_json({'trade_executed': False, 'error': 'Invalid API key'})
                    
            except Exception as e:
                self.send_json({'error': str(e), 'query': query})
            finally:
                conn.close()
        
        elif parsed.path == '/login':
            """Уязвимый login для HFT системы"""
            params = parse_qs(parsed.query)
            username = params.get('username', [''])[0]
            password = params.get('password', [''])[0]
            
            conn = self.init_db()
            cursor = conn.cursor()
            
            # УЯЗВИМЫЙ КОД - конкатенация строк!
            query = f"SELECT * FROM traders WHERE username='{username}' AND password='{password}'"
            
            start = time.perf_counter()
            try:
                cursor.execute(query)
                trader = cursor.fetchone()
                elapsed = time.perf_counter() - start
                
                self.send_json({
                    'authenticated': trader is not None,
                    'execution_time_ms': elapsed * 1000,
                    'username': username,
                    'query': query
                })
            except Exception as e:
                self.send_json({
                    'error': str(e),
                    'query': query
                })
            finally:
                conn.close()
        
        else:
            self.send_error(404)
    
    def send_json(self, data):
        """Отправка JSON с заголовками для HFT"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('X-HFT-Server', 'Vulnerable')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def log_message(self, format, *args):
        """Минимальное логирование для HFT"""
        pass

def run_hft_vulnerable_server(port=8888):
    """Запуск уязвимого HFT сервера"""
    import socket
    
    def check_port(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('127.0.0.1', port))
            sock.close()
            return True
        except:
            return False
    
    if not check_port(port):
        print(f"⚠️  Порт {port} занят! Пробую порт {port + 1}")
        port += 1
    
    try:
        server = HTTPServer(('127.0.0.1', port), HFTVulnerableSQLiServer)
        
        print("="*80)
        print("⚡ HFT УЯЗВИМЫЙ SQL INJECTION СЕРВЕР (TIMING-BASED)")
        print("="*80)
        print(f"📍 Адрес: http://127.0.0.1:{port}")
        print(f"🔓 Пароль трейдера: '{HFTVulnerableSQLiServer.SECRET_PASSWORD}'")
        print(f"⏱️  Задержка при успехе: 1 мс")
        
        print("\n🎯 УЯЗВИМОСТИ ДЛЯ HFT:")
        print("  1. Time-based SQL Injection через SLEEP/BENCHMARK")
        print("  2. Blind SQL Injection в торговых условиях")
        print("  3. Подбор API ключей через timing атаки")
        print("  4. Утечка данных через микросекундные задержки")
        
        print("\n📡 HFT ENDPOINTS:")
        print("  GET /info - информация о сервере")
        print("  GET /check?condition=SQL - timing проверка")
        print("  GET /market?condition=SQL - рыночные условия")
        print("  GET /trade?api_key=X&symbol=Y - выполнение сделки")
        print("  GET /login?username=X&password=Y - авторизация")
        
        print("\n💀 ПРИМЕРЫ АТАК:")
        print("  /check?condition=1=1 AND SLEEP(0.01)")
        print("  /market?condition=1=1 AND BENCHMARK(100000, MD5('test'))")
        print("  /check?condition=SUBSTR((SELECT password FROM traders WHERE username='admin'),1,1)='T'")
        print("="*80)
        print("\n🚀 Сервер запущен. Для остановки: Ctrl+C")
        print("="*80)
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n\n🛑 HFT сервер остановлен")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")

if __name__ == "__main__":
    run_hft_vulnerable_server()