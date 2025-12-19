"""Скрипт для запуска сервера разработки"""
from waitress import serve
from pyramid.paster import get_app
import sys
import io

# Исправляем кодировку для Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

if __name__ == '__main__':
    import socket
    
    # Получаем локальный IP адрес
    def get_local_ip():
        try:
            # Подключаемся к внешнему адресу, чтобы узнать локальный IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    local_ip = get_local_ip()
    app = get_app('development.ini', 'main')
    print("\n" + "="*60)
    print("[START] Запуск сервера Vols GIS...")
    print("="*60)
    print(f"Сервер доступен по адресам:")
    print(f"  - http://localhost:6543")
    print(f"  - http://127.0.0.1:6543")
    print(f"  - http://{local_ip}:6543")
    print("="*60)
    print("Нажмите Ctrl+C для остановки\n")
    serve(app, host='0.0.0.0', port=6543)

