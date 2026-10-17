# Student Grading System

Лабораторна робота №1 з курсу «Професійний Python».
Варіант №7 — «Система оцінювання студентів».

## Можливості

- зберігання ПІБ, дисципліни та списку оцінок студента;
- обчислення середнього бала, мінімальної та максимальної оцінок;
- визначення рівня успішності за 100-бальною шкалою;
- сортування студентів за середнім балом;
- пошук студентів із середнім балом вище заданого;
- пошук за частиною ПІБ, дисципліною та мінімальним середнім балом;
- загальна статистика для всіх записів;
- інтерактивне меню з перевіркою введених даних;
- демонстраційний режим, який завершується без очікування вводу.

## Шкала оцінювання

| Середній бал | Рівень |
| --- | --- |
| 90–100 | відмінно |
| 75–89,99 | добре |
| 60–74,99 | задовільно |
| 0–59,99 | незадовільно |

Оцінка повинна бути скінченним числом від 0 до 100. Усі межі винесені до
`src/student_grading/config.py`.

## Вимоги

- Python 3.11 або новіший;
- Git;
- `pytest` і `pytest-cov` для тестування, встановлюються через extra `test`.

## Встановлення

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

### Linux і macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[test]"
```

## Запуск

Демонстраційний режим виконує всі операції варіанта й завершується автоматично:

```bash
python -m student_grading
```

Пороговий бал для пошуку можна змінити:

```bash
python -m student_grading --threshold 85
```

Інтерактивне меню з введенням даних із клавіатури:

```bash
python -m student_grading --interactive
```

Після editable installation доступна також console command:

```bash
student-grading --interactive
```

## Приклад результату

```text
РЕЙТИНГ ЗА СЕРЕДНІМ БАЛОМ
ПІБ                      Дисципліна         Сер.   Мін.  Макс. Статус
----------------------------------------------------------------------------------
Ірина Бондар             Бази даних        96.25  94.00  98.00 відмінно
Анна Коваль              Python            91.50  88.00  95.00 відмінно

СЕРЕДНІЙ БАЛ ВИЩЕ 80
Анна Коваль              Python            91.50  88.00  95.00 відмінно
Ірина Бондар             Бази даних        96.25  94.00  98.00 відмінно
```

## Тести

```bash
python -m pytest
python -m pytest --cov=student_grading --cov-report=term-missing
```

Конфігурація в `pyproject.toml` вимагає не менше 90% покриття. Поточний
перевірений результат: 38 тестів пройдено, загальне покриття — 99,6%.

## Структура проєкту

```text
student-grading-system/
├── .gitignore
├── pyproject.toml
├── README.md
├── src/
│   └── student_grading/
│       ├── __init__.py
│       ├── __main__.py
│       ├── config.py
│       ├── exceptions.py
│       ├── main.py
│       ├── models.py
│       └── services.py
└── tests/
    ├── test_main.py
    ├── test_models.py
    └── test_services.py
```

`models.py` містить `dataclass StudentRecord`. `services.py` реалізує business
logic без залежності від консолі. `main.py` відповідає за виведення,
інтерактивне меню й application entry point. `config.py` містить константи,
а `exceptions.py` — власний виняток `GradeValidationError`.

## Автор

Денис Заставний.
