#!/usr/bin/env python
"""
Скрипт для тестирования API эндпоинтов
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_courses():
    """Тестирование API курсов"""
    print("=== Тестирование API курсов ===")
    
    print("\n1. Получение списка курсов:")
    response = requests.get(f"{BASE_URL}/courses/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    print("\n2. Создание курса:")
    course_data = {
        "title": "Python для начинающих",
        "description": "Изучаем основы программирования на Python"
    }
    response = requests.post(f"{BASE_URL}/courses/", json=course_data)
    print(f"Status: {response.status_code}")
    course_result = response.json()
    print(f"Response: {course_result}")
    
    if response.status_code == 201:
        course_id = course_result['id']
        
        print(f"\n3. Получение курса по ID ({course_id}):")
        response = requests.get(f"{BASE_URL}/courses/{course_id}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # 4. Обновление курса
        print(f"\n4. Обновление курса ({course_id}):")
        update_data = {
            "title": "Python для начинающих - Обновлено",
            "description": "Обновленное описание курса"
        }
        response = requests.put(f"{BASE_URL}/courses/{course_id}/", json=update_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        return course_id
    
    return None

def test_lessons(course_id):
    """Тестирование API уроков"""
    print("\n=== Тестирование API уроков ===")
    
    # 1. Получение списка уроков
    print("\n1. Получение списка уроков:")
    response = requests.get(f"{BASE_URL}/lessons/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # 2. Создание урока
    print("\n2. Создание урока:")
    lesson_data = {
        "title": "Введение в Python",
        "description": "Первые шаги в программировании",
        "video_url": "https://youtube.com/watch?v=example",
        "course": course_id
    }
    response = requests.post(f"{BASE_URL}/lessons/", json=lesson_data)
    print(f"Status: {response.status_code}")
    lesson_result = response.json()
    print(f"Response: {lesson_result}")
    
    if response.status_code == 201:
        lesson_id = lesson_result['id']
        
        # 3. Получение урока по ID
        print(f"\n3. Получение урока по ID ({lesson_id}):")
        response = requests.get(f"{BASE_URL}/lessons/{lesson_id}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # 4. Обновление урока
        print(f"\n4. Обновление урока ({lesson_id}):")
        update_data = {
            "title": "Введение в Python - Обновлено",
            "description": "Обновленное описание урока",
            "video_url": "https://youtube.com/watch?v=updated",
            "course": course_id
        }
        response = requests.put(f"{BASE_URL}/lessons/{lesson_id}/", json=update_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        return lesson_id
    
    return None

def test_course_lessons(course_id):
    """Тестирование получения уроков курса"""
    print(f"\n=== Тестирование получения уроков курса ({course_id}) ===")
    
    response = requests.get(f"{BASE_URL}/courses/{course_id}/lessons/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    try:
        print("Запуск тестирования API...")
        print("Убедитесь, что сервер Django запущен на http://127.0.0.1:8000")
        print("-" * 50)
        
        # Тестируем курсы
        course_id = test_courses()
        
        if course_id:
            # Тестируем уроки
            lesson_id = test_lessons(course_id)
            
            # Тестируем получение уроков курса
            test_course_lessons(course_id)
        
        print("\n" + "=" * 50)
        print("Тестирование завершено!")
        
    except requests.exceptions.ConnectionError:
        print("Ошибка: Не удается подключиться к серверу.")
        print("Убедитесь, что Django сервер запущен на http://127.0.0.1:8000")
    except Exception as e:
        print(f"Ошибка: {e}")
