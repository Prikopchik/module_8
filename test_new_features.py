#!/usr/bin/env python
"""
Скрипт для тестирования новых функций API
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_course_with_lessons():
    """Тестирование курса с уроками и количеством"""
    print("=== Тестирование курса с уроками ===")
    
    print("\n1. Получение списка курсов:")
    response = requests.get(f"{BASE_URL}/courses/")
    print(f"Status: {response.status_code}")
    courses = response.json()
    print(f"Количество курсов: {len(courses)}")
    
    if courses:
        course = courses[0]
        print(f"Курс: {course['title']}")
        print(f"Количество уроков: {course.get('lessons_count', 'N/A')}")
        print(f"Уроки: {len(course.get('lessons', []))}")
        
        print(f"\n2. Детальная информация о курсе {course['id']}:")
        response = requests.get(f"{BASE_URL}/courses/{course['id']}/")
        print(f"Status: {response.status_code}")
        course_detail = response.json()
        print(f"Курс: {course_detail['title']}")
        print(f"Количество уроков: {course_detail.get('lessons_count', 'N/A')}")
        print(f"Уроки:")
        for lesson in course_detail.get('lessons', []):
            print(f"  - {lesson['title']} (ID: {lesson['id']})")

def test_payments():
    """Тестирование API платежей"""
    print("\n=== Тестирование API платежей ===")
    
    print("\n1. Получение списка платежей:")
    response = requests.get(f"{BASE_URL}/users/payments/")
    print(f"Status: {response.status_code}")
    payments = response.json()
    print(f"Количество платежей: {len(payments)}")
    
    if payments:
        payment = payments[0]
        print(f"Первый платеж: {payment}")
    
    print("\n2. Фильтрация по способу оплаты (cash):")
    response = requests.get(f"{BASE_URL}/users/payments/?payment_method=cash")
    print(f"Status: {response.status_code}")
    cash_payments = response.json()
    print(f"Платежи наличными: {len(cash_payments)}")
    
    print("\n3. Фильтрация по способу оплаты (transfer):")
    response = requests.get(f"{BASE_URL}/users/payments/?payment_method=transfer")
    print(f"Status: {response.status_code}")
    transfer_payments = response.json()
    print(f"Платежи переводом: {len(transfer_payments)}")
    
    print("\n4. Сортировка по дате оплаты (по возрастанию):")
    response = requests.get(f"{BASE_URL}/users/payments/?ordering=payment_date")
    print(f"Status: {response.status_code}")
    sorted_payments = response.json()
    print(f"Платежи отсортированы по дате: {len(sorted_payments)}")
    if sorted_payments:
        print(f"Первый платеж: {sorted_payments[0]['payment_date']}")
        print(f"Последний платеж: {sorted_payments[-1]['payment_date']}")
    
    print("\n5. Сортировка по сумме (по убыванию):")
    response = requests.get(f"{BASE_URL}/users/payments/?ordering=-amount")
    print(f"Status: {response.status_code}")
    amount_sorted_payments = response.json()
    print(f"Платежи отсортированы по сумме: {len(amount_sorted_payments)}")
    if amount_sorted_payments:
        print(f"Самый большой платеж: {amount_sorted_payments[0]['amount']} руб.")
        print(f"Самый маленький платеж: {amount_sorted_payments[-1]['amount']} руб.")

def test_payment_filters():
    """Тестирование различных фильтров платежей"""
    print("\n=== Тестирование фильтров платежей ===")
    
    print("\n1. Получение курсов для фильтрации:")
    response = requests.get(f"{BASE_URL}/courses/")
    courses = response.json()
    if courses:
        course_id = courses[0]['id']
        print(f"Фильтрация по курсу ID {course_id}:")
        response = requests.get(f"{BASE_URL}/users/payments/?paid_course={course_id}")
        print(f"Status: {response.status_code}")
        course_payments = response.json()
        print(f"Платежи за курс: {len(course_payments)}")
    
    print("\n2. Получение уроков для фильтрации:")
    response = requests.get(f"{BASE_URL}/lessons/")
    lessons = response.json()
    if lessons:
        lesson_id = lessons[0]['id']
        print(f"Фильтрация по уроку ID {lesson_id}:")
        response = requests.get(f"{BASE_URL}/users/payments/?paid_lesson={lesson_id}")
        print(f"Status: {response.status_code}")
        lesson_payments = response.json()
        print(f"Платежи за урок: {len(lesson_payments)}")
    
    print("\n3. Фильтрация по сумме (больше 1000 руб.):")
    response = requests.get(f"{BASE_URL}/users/payments/?amount__gte=1000")
    print(f"Status: {response.status_code}")
    high_amount_payments = response.json()
    print(f"Платежи больше 1000 руб.: {len(high_amount_payments)}")
    
    print("\n4. Комбинированная фильтрация (наличные + больше 500 руб.):")
    response = requests.get(f"{BASE_URL}/users/payments/?payment_method=cash&amount__gte=500")
    print(f"Status: {response.status_code}")
    combined_payments = response.json()
    print(f"Платежи наличными больше 500 руб.: {len(combined_payments)}")

if __name__ == "__main__":
    try:
        print("Запуск тестирования новых функций API...")
        print("Убедитесь, что сервер Django запущен на http://127.0.0.1:8000")
        print("-" * 60)
        
        test_course_with_lessons()
        
        test_payments()
        
        test_payment_filters()
        
        print("\n" + "=" * 60)
        print("Тестирование новых функций завершено!")
        
    except requests.exceptions.ConnectionError:
        print("Ошибка: Не удается подключиться к серверу.")
        print("Убедитесь, что Django сервер запущен на http://127.0.0.1:8000")
    except Exception as e:
        print(f"Ошибка: {e}")
