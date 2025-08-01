# Прототип RAG-системы для ответов по технической документации нефтегазовой отрасли

---

## Описание этапов сбора и предобработки данных

Для создания базы данных было собрано 53 документа из электронного ресурса [OGBUS](http://www.ogbus.ru), выпуск №2 2012 год, специализирующегося на нефтегазовой тематике. Документы включают статьи и технические материалы, все на русском языке.

Тексты были извлечены и сохранены в едином текстовом файле формата `.txt`. Для каждого фрагмента текста дополнительно сохранялись метаданные: источник, название статьи и номер страницы, с которой был взят текст.

Далее текст был разбит на чанки заданной длины с перекрытием и сохранен в формат `.json`. При этом крайние слова в чанках отбрасывались, чтобы избежать их усечения и некорректного состава слов.

Для векторного индексирования чанков использовалась база ChromaDB, где хранились как эмбеддинги, так и метаданные каждого чанка.

---

## Этапы RAG

1. **Сбор данных:** Сбор документов из открытых отраслевых источников (в данном случае — OGBUS).
2. **Предобработка:** Конвертация документов в единый текстовый формат, очистка и сохранение метаданных.
3. **Деление на чанки:** Разбиение текста с перекрытием для более точного поиска.
4. **Векторное хранилище:** Индексация чанков с помощью ChromaDB.
5. **Retriever:** Поиск топ-5 релевантных чанков для заданного вопроса.
6. **Generator:** Генерация ответа на основе контекста из найденных чанков с помощью LLM (провайдер GigaChat).
7. **Фронтенд:** Веб-интерфейс на Streamlit для ввода вопросов и отображения ответов.

---

## Схема архитектуры RAG
![alt text](rag.jpg)
## Примеры запросов и ответов

1. **Вопрос:** Каковы основные требования к буровым растворам в нефтедобыче?  
   **Ответ:** Основные требования к буровым растворам в нефтедобыче включают:
    - Создание противодавления на стенки скважин для предотвращения потери устойчивости пород.
    - Поддержание стабильности растворов полимеров с течением времени, особенно их вязкости при различных температурах.
    - Повышение устойчивости стенок скважин, предотвращение обвалов и осыпей за счет использования силиката натрия.
    - Предотвращение коррозии забойных инструментов и обсадных колонн.
    - Возможность эффективного утяжеления для борьбы с проявлениями и поглощениями при бурении в условиях аномально-высокого порового давления.

2. **Вопрос:** Какие стандарты регулируют техническое обслуживание компрессоров?  
   **Ответ:** К сожалению, я не могу ответить на данный вопрос.

3. **Вопрос:** Каковы методы предотвращения коррозии в трубопроводах?  
   **Ответ:** Методы предотвращения коррозии в трубопроводах включают следующие подходы:
    - Использование средств электрохимической защиты (ЭХЗ).
    - Применение ингибиторов коррозии.
    - Нанесение изоляционных материалов.
    - Замена традиционных металлических труб на стеклопластиковые трубы, обладающие высокой стойкостью к коррозии.
    - Также актуальными остаются меры по борьбе с гидратообразованием через введение ингибиторов, таких как метанол.

4. **Вопрос:** Как происходит контроль качества нефти на добыче?  
   **Ответ:** К сожалению, я не могу ответить на данный вопрос.

5. **Вопрос:** Почему появляются фонтаны при бурении скважин?
   **Ответ:** Фонтаны при бурении скважин возникают вследствие превышения забойного давления (Pзаб) над пластовым давлением (Pпл), что создает разницу давлений (ΔP1). Это приводит к прорыву флюидов (нефть, газ) вверх по стволу скважины, особенно если пласт обладает высокой пористостью и проницаемостью. Отсутствие циркуляции бурового раствора усугубляет ситуацию, так как не создается гидравлическое сопротивление, препятствующее подъему газа и жидкости. Кроме того, на фоне низкого коэффициента поглощения в пластах с низкой проницаемостью создаются дополнительные напряжения, способствующие открытому выбросу углеводородов.

---

## Детальное обоснование выбора LLM

Для генерации ответов была выбрана модель провайдера **GigaChat** с тремя вариантами моделей: light, pro и max. Основные причины выбора:

- **Качество генерации:** Модели GigaChat показывают высокое качество генерации текстов. Ссылки на результаты: 
    - https://llmarena.ru/?leaderboard
    - https://developers.sber.ru/docs/ru/gigachat/models/updates
- **Производительность:** Использование API-решения позволило избежать необходимости локального развертывания тяжелых моделей, что важно при ограничениях по аппаратным ресурсам.
- **Соответствие задаче:** GigaChat предоставляет гибкие модели под разные задачи и нагрузку, что удобно при построении прототипа RAG. Легко масштабируется и интегрируется с пайплайном (langchain-gigachat, langhain-chroma).

Таким образом, преимущество было отдано облачному API-решению, что ускорило разработку и упростило поддержку.

---

## Дальнейшие перспективы


1. **Добавление реранкера**  
   После извлечения релевантных чанков планируется внедрение реранкера (например, Cross-Encoder), который улучшит порядок контекста и повысит точность ответов.

2. **Оптимизация разбиения на чанки**  
   Вместо фиксированной длины будет использоваться смысловое разбиение (по абзацам, предложениям) для сохранения логики текста и повышения качества поиска.

3. **Улучшение промптов для LLM**  
   Будут доработаны промпты: добавлены примеры, улучшено форматирование и адаптация под типы документов (стандарты, статьи и т.д.).

4. **Извлечение и обработка таблиц**  
   Планируется реализовать извлечение табличных данных из документов с помощью библиотеки **`unstructured`**, с преобразованием в текстовый вид для включения в поиск и генерацию ответов.

---

## Инструкция по запуску через GitHub

1. Клонируйте репозиторий и перейдите в его директорию:

   ```bash
   git clone https://github.com/MaratSabitov2002/oilgasrag.git
   cd oilgasrag

2. Установите зависимости:

    ```bash
    pip install -r requirements.txt

3. Установите пакет в режиме разработки:

    ```bash
    pip install -e .

4. Запустите приложение:

    ```bash
    python data/app.py
    
5. Откройте в браузере адрес, указанный в консоли (обычно http://localhost:8501) для работы с интерфейсом.
---

## Запуск через Docker

Для запуска приложения с использованием Docker выполните следующие шаги:

1. Скачайте Docker-образ

```bash
    docker pull maratsabitov/oilgasrag-app:latest
```

2. Подготовьте файл .env. Создайте файл .env, в котором укажите ваши ключи доступа к API моделей GigaChat. Пример содержимого:

```python

    GIGACHAT_API=your_api_key_here
    # example:
    # GIGACHAT_API=qwerty123
```
3. Запуск контейнера

```bash
    docker run -p 8501:8501 --env-file .env maratsabitov/oilgasrag-app
```

Если файл .env находится в другом месте, укажите путь явно:
```
docker run -p 8501:8501 --env-file /полный_путь_к/.env maratsabitov/oilgasrag-app
```
4. После запуска откройте браузер и перейдите по адресу http://localhost:8501

