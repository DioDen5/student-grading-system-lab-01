# Student Grading System

Наскрізний навчальний проєкт з курсу «Професійний Python».

- Студент: Заставний Денис
- Група: ФеП-32
- Варіант: 7
- Предметна область: система оцінювання студентів
- Реалізовані роботи: Лабораторна робота №1 і Лабораторна робота №2

## Лабораторна робота №2

Тема: «Структури даних та функціональна декомпозиція».

Кожний запис містить ID, ПІБ, групу, дисципліну та незмінний `tuple` оцінок.
Програма реалізує всі операції варіанта 7:

- середній бал, мінімальну та максимальну оцінки кожного студента;
- визначення успішності за 100-бальною шкалою;
- сортування за середнім балом і фільтрацію за заданим порогом;
- групування за дисциплінами та вкладене групування за дисципліною і групою;
- `Counter` дисциплін і оцінок;
- `dict`-індекси за ID та нормалізованим ПІБ;
- пошук у `list` зі складністю O(n) і в `dict` у середньому O(1);
- агрегацію статистики за дисциплінами;
- універсальні filter, sort і processing pipeline;
- closure для створення фільтрів;
- параметризований decorator із `*args`, `**kwargs` та історією в `deque`;
- експорт підсумку в JSON;
- benchmark `list` проти `dict` на 1 000, 10 000 і 100 000 записів.

У коді явно використано `list`, `tuple`, `set`, `dict`, `Counter`,
`defaultdict`, `deque`, list/set/dict comprehensions, generator expressions,
lambda та функції вищого порядку.

## Шкала оцінювання

| Середній бал | Рівень |
| --- | --- |
| 90-100 | відмінно |
| 75-89,99 | добре |
| 60-74,99 | задовільно |
| 0-59,99 | незадовільно |

Оцінка повинна бути скінченним числом від 0 до 100. Межі зберігаються у
`src/student_grading/config.py`.

## Встановлення

Потрібні Python 3.11 або новіший і Git.

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

Повна демонстрація операцій варіанта 7:

```bash
python -m student_grading --threshold 80
```

Інтерактивне меню:

```bash
python -m student_grading --interactive
```

Обов'язковий benchmark для ЛР2:

```bash
python -m student_grading --benchmark
```

Експорт JSON-підсумку:

```bash
python -m student_grading --export-summary output/summary.json
```

Після editable installation доступна також команда `student-grading`.

## Аналіз складності

| Операція | Структура | Складність |
| --- | --- | --- |
| Лінійний пошук студента за ID | `list` | O(n) |
| Побудова індексу | `dict` comprehension | O(n) |
| Пошук студента за ID після індексації | `dict` | O(1) у середньому |
| Перевірка наявності дисципліни | `set` | O(1) у середньому |
| Сортування студентів | `list`/Timsort | O(n log n) |
| Групування та агрегація | `defaultdict`/`dict` | O(n) |

Фактичні значення benchmark залежать від комп'ютера. Контрольний запуск
показує лінійне зростання часу пошуку в `list`, тоді як час пошуку в готовому
`dict` майже не змінюється зі збільшенням кількості записів.

## Тести

```bash
python -m pytest
python -m pytest --cov=student_grading --cov-report=term-missing
```

Поточний перевірений результат: 62 тести пройдено, загальне покриття - 99,8%.
Налаштований мінімальний поріг покриття - 90%.

## Структура проєкту

```text
student-grading-system/
├── .gitignore
├── pyproject.toml
├── README.md
├── report/
│   └── Звіт_ЛР02_варіант_7.docx
├── Lab_02/
│   └── report/
│       └── report.docx
├── docs/
│   ├── Lab_01_Report_Variant_7.docx
│   └── screenshots/
├── src/student_grading/
│   ├── __init__.py
│   ├── __main__.py
│   ├── analytics.py
│   ├── benchmark.py
│   ├── config.py
│   ├── data.py
│   ├── decorators.py
│   ├── exceptions.py
│   ├── main.py
│   ├── models.py
│   ├── processors.py
│   └── services.py
└── tests/
    ├── test_analytics.py
    ├── test_benchmark.py
    ├── test_decorators.py
    ├── test_main.py
    ├── test_models.py
    ├── test_processors.py
    └── test_services.py
```

## Автор

Заставний Денис, група ФеП-32, варіант 7.
