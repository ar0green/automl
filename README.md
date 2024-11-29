# AutoMLPipeline

Этот маленький пет-проект представляет собой AutoML-пайплайн для задач классификации и регрессии. Он автоматически выбирает лучшие модели и гиперпараметры с использованием `Optuna`, логирует эксперименты с помощью `MLflow` и "предоставляет" API для дальнейшего использования в продуктиве через `FastAPI`.

## **Возможности**

- Поддержка моделей: Random Forest, XGBoost, LightGBM, LogReg, LinReg
- Автоматическая оптимизация гиперпараметров
- Поддержка задач классификации и регрессии
- Логирование экспериментов с помощью MLflow
- REST API для использования модели
- "Гибкая" предобработка данных

## **Установка**

1. **Клонируйте репозиторий:**

   ```bash
   git clone https://github.com/yourusername/AutoMLPipeline.git
   cd AutoMLPipeline
   ```

2. **Создайте виртуальное окружение и активируйте его**:

    Для Linux/Mac
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
    Для Windows
    ```bash
    python -m venv venv
    venv\Scripts\activate   
    ```
3. **Установите зависимости:**

    ```bash
    pip install -r requirements.txt
    ```

## **Использование**

1. **Обучение модели**

    1. Поместите ваши датасеты в папку data/.
    2. Обновите main.py с информацией о вашем датасете:
        - Путь к файлу данных
        - Названия столбцов
        - Название целевой переменной
        - Тип задачи (classification или regression)
        - Разделитель в файле данных
    3. Запустите обучение:
        ```bash
        python main.py
        ```

    TODO: запуск через pipeline.py, запуск обучения через интерфейс REST API
2. **Запуск REST API**
    
    1. Проверьте, что после обучения - модель сохранена в папке models/{dataset_name}_{model_name}/.

    2. Запустите приложение FastAPI:

        ```bash
        # проверьте, что вы в корневой директории проекта
        uvicorn app:app --reload
        ```
        После запуска "приложение" будет доступно по адресу http://localhost:8000.

    3.Тестирование API:

    - Через браузер:
        
        Перейдите по адресу http://localhost:8000/docs, чтобы открыть автоматически сгенерированную документацию Swagger UI.

    - Через терминал:

        ```bash
        curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" -d "{\"features\": [5.1, 3.5, 1.4, 0.2]}"
        ```
    - Через обычный REST запрос:

        POST /predict
        ```json
        {
        "features": [5.1, 3.5, 1.4, 0.2],
        "model_name": "iris_model"
        }
        ```

## **Развертывание с помощью Docker**

1. Docker-образ:

    ```bash
    docker build -t automl-api .
    ```

2. Запустите контейнер:

    ```bash
    docker run -d -p 8000:8000 automl-api
    ```

    Теперь API доступен по адресу http://localhost:8000.

### Примеры использования

Запрос к API для получения предсказания POST /predict
```json
{
  "features": [5.1, 3.5, 1.4, 0.2],
  "model_name": "iris_model"
}
```

Ответ:

```json
{
"prediction": [0]
}
