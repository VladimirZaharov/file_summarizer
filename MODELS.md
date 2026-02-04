# Рекомендации по моделям OpenRouter

## ✅ Для документов используйте ТЕКСТОВЫЕ модели

### Лучшие модели для суммаризации документов:

```bash
# 1. Google Gemma (РЕКОМЕНДУЕТСЯ)
--model google/gemma-2-9b-it:free
# Лучшее качество для документов, хорошая скорость

# 2. Google Gemini Flash
--model google/gemini-flash-1.5:free
# Очень быстрая, хорошее качество

# 3. Meta Llama
--model meta-llama/llama-3.2-3b-instruct:free
# Хорошее качество, средняя скорость

# 4. Qwen
--model qwen/qwen-2-7b-instruct:free
# Альтернатива с хорошим качеством

# 5. Mistral
--model mistralai/mistral-7b-instruct:free
# Надежная модель с хорошей производительностью
```

## ❌ НЕ используйте эти модели для документов:

```bash
# allenai/molmo-2-8b:free
# ❌ Это MULTIMODAL модель для изображений и видео
# ❌ НЕ может читать документы из Google Drive URL
# ❌ Вызовет ошибку 502 Bad Gateway
```

## Почему ошибка 502 с molmo?

**Проблема:**
- `allenai/molmo-2-8b:free` - это модель для обработки изображений/видео
- Она пытается загрузить Google Drive URL как изображение
- Google Drive не отдаёт файлы напрямую по ссылке без авторизации
- Результат: **502 Bad Gateway**

**Решение:**
1. Использовать **текстовые модели** (gemma, gemini, llama)
2. Использовать **[`summarize_download.py`](summarize_download.py:1)** который:
   - Скачивает файлы
   - Извлекает текст локально
   - Отправляет текст в модель

## Примеры использования

### Правильно ✅

```bash
# С Gemma (лучшее качество)
python summarize_download.py \
    --file-list file_ids.txt \
    --model google/gemma-2-9b-it:free

# С Gemini Flash (быстрее)
python summarize_download.py \
    --file-list file_ids.txt \
    --model google/gemini-flash-1.5:free

# По умолчанию (gemma)
python summarize_download.py --file-list file_ids.txt
```

### Неправильно ❌

```bash
# НЕ делайте так!
python summarize_download.py \
    --file-list file_ids.txt \
    --model allenai/molmo-2-8b:free  # ❌ Ошибка 502!
```

## Сравнение моделей

| Модель | Качество | Скорость | Для документов |
|--------|----------|----------|----------------|
| google/gemma-2-9b-it:free | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Отлично |
| google/gemini-flash-1.5:free | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Отлично |
| meta-llama/llama-3.2-3b-instruct:free | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ Хорошо |
| qwen/qwen-2-7b-instruct:free | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ Хорошо |
| mistralai/mistral-7b-instruct:free | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Хорошо |
| allenai/molmo-2-8b:free | N/A | N/A | ❌ НЕТ (для изображений) |

## Как выбрать модель?

**Для максимального качества:**
```bash
--model google/gemma-2-9b-it:free
```

**Для максимальной скорости:**
```bash
--model google/gemini-flash-1.5:free
```

**Для баланса качество/скорость:**
```bash
--model mistralai/mistral-7b-instruct:free
```

## Rate Limits

Все бесплатные модели имеют ограничения:
- Обычно ~20 запросов в минуту
- Если достигли лимита - подождите 60 секунд
- Или переключитесь на другую модель

## Дополнительные ресурсы

- [Список всех моделей OpenRouter](https://openrouter.ai/models)
- [Документация OpenRouter](https://openrouter.ai/docs)
- Фильтр по бесплатным: https://openrouter.ai/models?pricing=free
