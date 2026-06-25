from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import requests
import time
import os

# =============================================
# НАСТРОЙКИ (ЗАМЕНИТЕ ТОКЕН ПРИ НЕОБХОДИМОСТИ)
# =============================================
VK_TOKEN = "vk1.a.zvmyX3JIcBltHnYu4lrveJDWoAJyRk4ouUB14_0mnILjcOZQ-OPjkQ7ijgI8CogPZ6BjgufKMdRXo5mxHsOaOV0FEPTVyukm1umDde-7LZPpfHTBIOggYFFgz9Ee9HK6LrtLqFmop0Vs7DRlL3NjYNMDM9IriuOsCw32pgxu_jnjCe3YUFfUeb8MGeXWJLkYDiImzevw4_QXi0VH5Tgblg"
CHAT_ID = 2000000001
# =============================================

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path != '/send':
            self.send_response(404)
            self.end_headers()
            return

        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            print(f"📩 Заявка с сайта:")
            print(f"   👤 Имя: {data.get('name', '—')}")
            print(f"   📞 Телефон: {data.get('phone', '—')}")
            print(f"   📍 Точка: {data.get('pickupPoint', '—')}")
            print(f"   ⏰ Время: {data.get('pickupTime', '—')}")
            print(f"   📝 Комментарий: {data.get('comment', '—')}")
            print(f"   📞 Связь с бариста: {data.get('callbackConsent', 'Нет')}")
            print(f"   ✅ Согласие на ПД: {data.get('personalDataConsent', 'Нет')}")

            message = f"""📦 НОВЫЙ ПРЕДЗАКАЗ

👤 Имя: {data.get('name', '—')}
📞 Телефон: {data.get('phone', '—')}
📍 Точка самовывоза: {data.get('pickupPoint', '—')}
⏰ Время самовывоза: {data.get('pickupTime', '—')}
📝 Комментарий: {data.get('comment', '—')}
📞 Связь с бариста: {data.get('callbackConsent', 'Нет')}
✅ Согласие на обработку ПД: {data.get('personalDataConsent', 'Нет')}
🕐 Время заявки: {time.strftime('%d.%m.%Y %H:%M')}
"""

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

            if result.get('error'):
                error_msg = result['error'].get('error_msg', 'Неизвестная ошибка')
                print(f"❌ Ошибка VK: {error_msg}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': error_msg}).encode())
            else:
                print("✅ Заявка отправлена в VK!")
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    host = '0.0.0.0'
    
    print("=" * 50)
    print("🚀 СЕРВЕР ДЛЯ ПРЕДЗАКАЗОВ")
    print("=" * 50)
    print(f"✅ VK Token: {VK_TOKEN[:20]}...")
    print(f"✅ Chat ID: {CHAT_ID}")
    print(f"✅ Сервер запущен на {host}:{port}")
    print("📨 Ожидание заявок...")
    print("=" * 50)
    
    server = HTTPServer((host, port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")
        server.shutdown()
