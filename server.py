from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import requests
import time

# =============================================
# НАСТРОЙКИ (ЗАМЕНИТЕ ТОКЕН ПРИ НЕОБХОДИМОСТИ)
# =============================================
VK_TOKEN = "vk1.a.zvmyX3JIcBltHnYu4lrveJDWoAJyRk4ouUB14_0mnILjcOZQ-OPjkQ7ijgI8CogPZ6BjgufKMdRXo5mxHsOaOV0FEPTVyukm1umDde-7LZPpfHTBIOggYFFgz9Ee9HK6LrtLqFmop0Vs7DRlL3NjYNMDM9IriuOsCw32pgxu_jnjCe3YUFfUeb8MGeXWJLkYDiImzevw4_QXi0VH5Tgblg"

# ID ВАШЕЙ БЕСЕДЫ (из get_chat_id.py)
CHAT_ID = 2000000001
# =============================================

class Handler(BaseHTTPRequestHandler):
    """
    Обработчик HTTP-запросов от сайта.
    Принимает POST-запросы на /send и отправляет их в VK.
    """
    
    def do_OPTIONS(self):
        """Обработка preflight-запросов CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """Обработка POST-запросов с заявками"""
        if self.path != '/send':
            self.send_response(404)
            self.end_headers()
            return

        try:
            # 1. Получаем данные от сайта
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            print(f"📩 Получена заявка с сайта:")
            print(f"   👤 Имя: {data.get('name', '—')}")
            print(f"   📞 Телефон: {data.get('phone', '—')}")
            print(f"   📍 Точка: {data.get('pickupPoint', '—')}")
            print(f"   📝 Комментарий: {data.get('comment', '—')}")
            print(f"   📞 Связь с бариста: {data.get('callbackConsent', 'Нет')}")
            print(f"   ✅ Согласие на ПД: {data.get('personalDataConsent', 'Нет')}")

            # 2. Формируем сообщение для VK
            message = f"""📦 НОВЫЙ ПРЕДЗАКАЗ

👤 Имя: {data.get('name', '—')}
📞 Телефон: {data.get('phone', '—')}
📍 Точка самовывоза: {data.get('pickupPoint', '—')}
📝 Комментарий: {data.get('comment', '—')}
📞 Связь с бариста: {data.get('callbackConsent', 'Нет')}
✅ Согласие на обработку ПД: {data.get('personalDataConsent', 'Нет')}
🕐 Время: {time.strftime('%d.%m.%Y %H:%M')}
"""

            # 3. Отправляем в VK
            url = 'https://api.vk.com/method/messages.send'
            params = {
                'access_token': VK_TOKEN,
                'v': '5.131',
                'peer_id': CHAT_ID,
                'message': message,
                'random_id': int(time.time())
            }

            response = requests.get(url, params=params)
            result = response.json()

            # 4. Обрабатываем ответ VK
            if result.get('error'):
                error_msg = result['error'].get('error_msg', 'Неизвестная ошибка')
                error_code = result['error'].get('error_code', '')
                print(f"❌ Ошибка VK API (код {error_code}): {error_msg}")
                
                # Отправляем ошибку обратно на сайт
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': error_msg,
                    'error_code': error_code
                }).encode())
            else:
                print("✅ Заявка успешно отправлена в беседу VK!")
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())

        except json.JSONDecodeError as e:
            print(f"❌ Ошибка парсинга JSON: {e}")
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Неверный формат данных'}).encode())

        except Exception as e:
            print(f"❌ Критическая ошибка сервера: {e}")
            import traceback
            traceback.print_exc()
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

# =============================================
# ЗАПУСК СЕРВЕРА
# =============================================
if __name__ == '__main__':
    print("=" * 50)
    print("🚀 СЕРВЕР ДЛЯ ПРЕДЗАКАЗОВ")
    print("=" * 50)
    print(f"✅ VK Token: {VK_TOKEN[:20]}...")
    print(f"✅ Chat ID: {CHAT_ID}")
    print(f"✅ Сервер запущен на http://localhost:8000")
    print(f"📨 Ожидание заявок...")
    print("=" * 50)
    print("Для остановки сервера нажмите Ctrl+C")
    print("=" * 50)
    
    server = HTTPServer(('localhost', 8000), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен пользователем")
        server.shutdown()