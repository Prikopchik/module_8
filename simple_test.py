import requests
import json

def test_api():
    try:
        print("Тестирование курсов...")
        response = requests.get("http://127.0.0.1:8000/api/courses/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Курсы: {len(data)}")
            if data:
                course = data[0]
                print(f"Первый курс: {course.get('title', 'N/A')}")
                print(f"Количество уроков: {course.get('lessons_count', 'N/A')}")
        else:
            print(f"Error: {response.text}")
        
        print("\nТестирование платежей...")
        response = requests.get("http://127.0.0.1:8000/api/users/payments/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Платежи: {len(data)}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    test_api()