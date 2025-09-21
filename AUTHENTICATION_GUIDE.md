
###  CRUD для пользователей
Регистрация: `POST /users/register/` (доступно без авторизации)
Вход: `POST /users/login/` (доступно без авторизации)
Выход: `POST /users/logout/` (требует авторизации)
Просмотр профиля: `GET /users/users/` (только свой профиль)
Обновление профиля: `PUT/PATCH /users/users/{id}/` (только свой профиль)
Удаление профиля: `DELETE /users/users/{id}/` (только свой профиль)

## API Endpoints

### Аутентификация
```
POST /users/register/          # Регистрация
POST /users/login/             # Вход
POST /users/logout/            # Выход
POST /users/token/             # Получение токена (стандартный JWT)
POST /users/token/refresh/     # Обновление токена
```

### Пользователи
```
GET    /users/users/           # Список пользователей (только свой профиль)
POST   /users/users/           # Создание пользователя
GET    /users/users/{id}/      # Детали пользователя
PUT    /users/users/{id}/      # Обновление пользователя
PATCH  /users/users/{id}/      # Частичное обновление
DELETE /users/users/{id}/      # Удаление пользователя
```

### Курсы
```
GET    /lms/courses/           # Список курсов (свои или все для модераторов)
POST   /lms/courses/           # Создание курса (только владельцы)
GET    /lms/courses/{id}/      # Детали курса
PUT    /lms/courses/{id}/      # Обновление курса
PATCH  /lms/courses/{id}/      # Частичное обновление
DELETE /lms/courses/{id}/      # Удаление курса (только владельцы)
GET    /lms/courses/{id}/lessons/  # Уроки курса
```

### Уроки
```
GET    /lms/lessons/           # Список уроков (свои или все для модераторов)
POST   /lms/lessons/           # Создание урока (только владельцы)
GET    /lms/lessons/{id}/      # Детали урока
PUT    /lms/lessons/{id}/      # Обновление урока
PATCH  /lms/lessons/{id}/      # Частичное обновление
DELETE /lms/lessons/{id}/      # Удаление урока (только владельцы)
```

### Платежи
```
GET    /users/payments/        # Список платежей (только свои)
POST   /users/payments/        # Создание платежа
GET    /users/payments/{id}/   # Детали платежа
PUT    /users/payments/{id}/   # Обновление платежа
PATCH  /users/payments/{id}/   # Частичное обновление
DELETE /users/payments/{id}/   # Удаление платежа
```
