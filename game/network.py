"""
Сетевой модуль для мультиплеера
Поддерживает сервер (хост) и клиент
"""
import socket
import threading
import json
import time
from typing import Optional, Callable, Dict, Any

class NetworkServer:
    """Сервер для мультиплеера (хост)"""
    def __init__(self, port: int = 12345):
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None
        self.client_address = None
        self.is_running = False
        self.receive_thread: Optional[threading.Thread] = None
        self.on_message: Optional[Callable] = None
        self.lobby_code = None
        
    def generate_lobby_code(self) -> str:
        """Генерирует код лобби из 6 цифр"""
        import random
        self.lobby_code = f"{random.randint(100000, 999999)}"
        return self.lobby_code
    
    def start(self) -> bool:
        """Запускает сервер"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('0.0.0.0', self.port))
            self.socket.listen(1)
            self.socket.settimeout(1.0)  # Таймаут для проверки is_running
            self.is_running = True
            
            # Запускаем поток для принятия подключений
            accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
            accept_thread.start()
            
            return True
        except Exception as e:
            print(f"Ошибка запуска сервера: {e}")
            return False
    
    def _accept_connections(self):
        """Принимает подключения клиентов"""
        while self.is_running:
            try:
                if self.client_socket is None:
                    client, address = self.socket.accept()
                    self.client_socket = client
                    self.client_address = address
                    print(f"Клиент подключен: {address}")
                    
                    # Запускаем поток для приема сообщений от клиента
                    self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
                    self.receive_thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.is_running:
                    print(f"Ошибка принятия подключения: {e}")
                break
    
    def _receive_messages(self):
        """Принимает сообщения от клиента"""
        buffer = b''
        while self.is_running and self.client_socket:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    print("[Сервер] Клиент отключился")
                    break
                buffer += data
                # Обрабатываем все полные сообщения (разделенные \n)
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    if line:
                        try:
                            message = json.loads(line.decode('utf-8'))
                            print(f"[Сервер] Получено сообщение: {message.get('type', 'unknown')}")
                            if self.on_message:
                                self.on_message(message)
                            else:
                                print("[Сервер] ОШИБКА: Обработчик сообщений не установлен!")
                        except json.JSONDecodeError as e:
                            print(f"[Сервер] Ошибка парсинга JSON: {e}, данные: {line}")
            except Exception as e:
                if self.is_running:
                    print(f"[Сервер] Ошибка приема сообщения: {e}")
                break
        
        # Клиент отключился
        self.client_socket = None
        self.client_address = None
        print("[Сервер] Поток приема сообщений завершен")
    
    def send(self, message: Dict[str, Any]):
        """Отправляет сообщение клиенту"""
        if self.client_socket:
            try:
                data = json.dumps(message).encode('utf-8')
                # Добавляем разделитель для надежной передачи
                data_with_separator = data + b'\n'
                sent = self.client_socket.send(data_with_separator)
                if sent > 0:
                    print(f"[Сервер] Отправлено сообщение: {message.get('type', 'unknown')}, размер: {sent} байт")
                    return True
                else:
                    print(f"[Сервер] ОШИБКА: Не удалось отправить сообщение")
                    return False
            except Exception as e:
                print(f"[Сервер] Ошибка отправки сообщения: {e}")
        else:
            print(f"[Сервер] ОШИБКА: Клиент не подключен! client_socket={self.client_socket}")
        return False
    
    def stop(self):
        """Останавливает сервер"""
        self.is_running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None


class NetworkClient:
    """Клиент для мультиплеера"""
    def __init__(self, host: str = 'localhost', port: int = 12345):
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.is_connected = False
        self.receive_thread: Optional[threading.Thread] = None
        self.on_message: Optional[Callable] = None
    
    def connect(self) -> bool:
        """Подключается к серверу"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(None)
            self.is_connected = True
            
            # Запускаем поток для приема сообщений
            self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.receive_thread.start()
            
            return True
        except Exception as e:
            print(f"Ошибка подключения к серверу: {e}")
            return False
    
    def _receive_messages(self):
        """Принимает сообщения от сервера"""
        buffer = b''
        while self.is_connected and self.socket:
            try:
                data = self.socket.recv(4096)
                if not data:
                    print("[Клиент] Соединение закрыто сервером")
                    break
                buffer += data
                # Обрабатываем все полные сообщения (разделенные \n)
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    if line:
                        try:
                            message = json.loads(line.decode('utf-8'))
                            print(f"[Клиент] Получено сообщение: {message.get('type', 'unknown')}")
                            if self.on_message:
                                self.on_message(message)
                            else:
                                print("[Клиент] ОШИБКА: Обработчик сообщений не установлен!")
                        except json.JSONDecodeError as e:
                            print(f"[Клиент] Ошибка парсинга JSON: {e}, данные: {line}")
            except Exception as e:
                if self.is_connected:
                    print(f"[Клиент] Ошибка приема сообщения: {e}")
                break
        
        # Отключились от сервера
        self.is_connected = False
        print("[Клиент] Поток приема сообщений завершен")
    
    def send(self, message: Dict[str, Any]):
        """Отправляет сообщение серверу"""
        if self.socket and self.is_connected:
            try:
                data = json.dumps(message).encode('utf-8')
                # Добавляем разделитель для надежной передачи
                data_with_separator = data + b'\n'
                sent = self.socket.send(data_with_separator)
                if sent > 0:
                    print(f"[Клиент] Отправлено сообщение: {message.get('type', 'unknown')}, размер: {sent} байт")
                    return True
                else:
                    print(f"[Клиент] ОШИБКА: Не удалось отправить сообщение")
                    return False
            except Exception as e:
                print(f"[Клиент] Ошибка отправки сообщения: {e}")
                self.is_connected = False
        else:
            print(f"[Клиент] ОШИБКА: Сокет не подключен! socket={self.socket}, is_connected={self.is_connected}")
        return False
    
    def disconnect(self):
        """Отключается от сервера"""
        self.is_connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

