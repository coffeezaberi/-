import requests

TOKEN = "vk1.a.zvmyX3JIcBltHnYu4lrveJDWoAJyRk4ouUB14_0mnILjcOZQ-OPjkQ7ijgI8CogPZ6BjgufKMdRXo5mxHsOaOV0FEPTVyukm1umDde-7LZPpfHTBIOggYFFgz9Ee9HK6LrtLqFmop0Vs7DRlL3NjYNMDM9IriuOsCw32pgxu_jnjCe3YUFfUeb8MGeXWJLkYDiImzevw4_QXi0VH5Tgblg"

url = 'https://api.vk.com/method/messages.getConversations'
params = {
    'access_token': TOKEN,
    'v': '5.131',
    'count': 10
}

response = requests.get(url, params=params)
result = response.json()

if result.get('response'):
    print("\n📋 ВАШИ БЕСЕДЫ:\n" + "=" * 40)
    for item in result['response']['items']:
        conversation = item['conversation']
        peer = conversation['peer']
        peer_id = peer['id']
        
        # Получаем название беседы
        title = conversation.get('chat_settings', {}).get('title', 'Без названия')
        
        print(f"📌 Название: {title}")
        print(f"   Peer ID: {peer_id}")
        print(f"   Тип: {peer['type']}")
        print("-" * 40)
else:
    print("❌ Ошибка:", result.get('error', 'Неизвестная ошибка'))