#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API с JWT авторизацией
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_register():
    """Тест регистрации пользователя"""
    print("=== Тест регистрации ===")
    
    data = {
        "email": "test@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(f"{BASE_URL}/users/register/", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        return response.json()['tokens']['access']
    return None

def test_login():
    """Тест входа пользователя"""
    print("\n=== Тест входа ===")
    
    data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/users/login/", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        return response.json()['tokens']['access']
    return None

def test_create_course(token):
    """Тест создания курса"""
    print("\n=== Тест создания курса ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": "Test Course",
        "description": "Test course description"
    }
    
    response = requests.post(f"{BASE_URL}/lms/courses/", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        return response.json()['id']
    return None

def test_create_lesson(token, course_id):
    """Тест создания урока"""
    print("\n=== Тест создания урока ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": "Test Lesson",
        "description": "Test lesson description",
        "video_url": "https://example.com/video",
        "course": course_id
    }
    
    response = requests.post(f"{BASE_URL}/lms/lessons/", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        return response.json()['id']
    return None

def test_list_courses(token):
    """Тест получения списка курсов"""
    print("\n=== Тест получения курсов ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/lms/courses/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_list_lessons(token):
    """Тест получения списка уроков"""
    print("\n=== Тест получения уроков ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/lms/lessons/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_unauthorized_access():
    """Тест доступа без авторизации"""
    print("\n=== Тест неавторизованного доступа ===")
    
    response = requests.get(f"{BASE_URL}/lms/courses/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def main():
    print("Запуск тестов API с JWT авторизацией")
    print("=" * 50)
    
    # Тест неавторизованного доступа
    test_unauthorized_access()
    
    # Регистрация и получение токена
    token = test_register()
    if not token:
        print("Ошибка регистрации, попробуем войти...")
        token = test_login()
    
    if not token:
        print("Не удалось получить токен авторизации")
        return
    
    # Тесты с авторизацией
    test_list_courses(token)
    test_list_lessons(token)
    
    course_id = test_create_course(token)
    if course_id:
        test_create_lesson(token, course_id)
    
    test_list_courses(token)
    test_list_lessons(token)

if __name__ == "__main__":
    main()
