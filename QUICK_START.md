# Quick Start - Document Summarizer

Простая инструкция для суммаризации документов из Google Drive без скачивания.

## Для публичных папок (БЕЗ авторизации)

### Шаг 1: Получить File IDs

1. Откройте папку в браузере: https://drive.google.com/drive/folders/1x6EKNkVw6PlFVTr6cGrsVscmRuwqGrXd
2. Кликните на каждый файл
3. Скопируйте ID из URL: `https://drive.google.com/file/d/FILE_ID_HERE/view`

Пример URLs и где найти ID:
- `https://drive.google.com/file/d/1abc123XYZ456def/view` → ID: `1abc123XYZ456def`

### Шаг 2: Создать file_ids.txt

Создайте текстовый файл `file_ids.txt` со списком ID (один на строку):

```
1abc123XYZ456def
2xyz789ABC012ghi
3mno345PQR678stu
```

### Шаг 3: Установить зависимости

```bash
cd python
pip install -r requirements.txt
```

### Шаг 4: Получить API ключ

1. Зарегистрируйтесь (бесплатно): https://openrouter.ai/
2. Получите API ключ
3. Установите:

```bash
export OPENROUTER_API_KEY=your_key_here
```

### Шаг 5: Запустить

```bash
# Из файла с IDs
python summarize_public.py --file-list file_ids.txt

# Или напрямую с IDs
python summarize_public.py --file-ids ID1 ID2 ID3

# С пользовательскими параметрами
python summarize_public.py \
    --file-list file_ids.txt \
    --model google/gemini-flash-1.5:free \
    --output my_summary.json
```

## Результат

Программа создаст JSON файл с:
- Саммари каждого документа
- Общий мастер-саммари всех документов
- Статистику

Пример вывода:

```
============================================================
SUMMARY STATISTICS
============================================================
Total Documents: 5
Successful: 5
Failed: 0

============================================================
MASTER SUMMARY
============================================================

This collection of documents covers the following main topics:

1. [Topic 1] - Key information about...
2. [Topic 2] - Important details regarding...
3. [Topic 3] - Analysis of...

Overall, these documents provide comprehensive information about...

============================================================
```

## Troubleshooting

### "API Error: 401"
- Проверьте API ключ
- Убедитесь что `export OPENROUTER_API_KEY=your_key` выполнен

### "File not accessible"
- Убедитесь что файлы публичные (Anyone with the link can view)
- Проверьте правильность File IDs

### "Rate limit exceeded"
- Подождите несколько секунд
- Попробуйте другую бесплатную модель

## Доступные модели (бесплатные)

```bash
# Gemini Flash (быстрая)
--model google/gemini-flash-1.5:free

# Gemma (хорошее качество)
--model google/gemma-2-9b-it:free

# Llama (альтернатива)
--model meta-llama/llama-3.2-3b-instruct:free

# Qwen (еще одна опция)
--model qwen/qwen-2-7b-instruct:free
```

## Альтернативный метод (с Google Drive API)

Если нужно работать с приватными папками, см. [`GDRIVE_SETUP.md`](GDRIVE_SETUP.md)

## Пример для практической задачи

Для папки: `https://drive.google.com/drive/folders/1x6EKNkVw6PlFVTr6cGrsVscmRuwqGrXd`

1. Откройте папку, извлеките все File IDs
2. Создайте `task_file_ids.txt`:
```
<список ваших file IDs>
```

3. Запустите:
```bash
export OPENROUTER_API_KEY=your_key_here
python summarize_public.py --file-list task_file_ids.txt --output task_summary.json
```

4. Результат будет в `task_summary.json`

## Структура JSON отчета

```json
{
  "master_summary": "Общий обзор всех документов...",
  "statistics": {
    "total_documents": 5,
    "successful_summaries": 5,
    "failed_summaries": 0
  },
  "individual_summaries": [
    {
      "filename": "document_1",
      "url": "https://drive.google.com/uc?id=...",
      "file_id": "...",
      "summary": "Краткое содержание документа...",
      "summary_status": "success"
    }
  ],
  "metadata": {
    "generated_at": "2026-02-04T08:53:00",
    "model_used": "google/gemini-flash-1.5:free",
    "total_files": 5,
    "method": "public_file_ids"
  }
}
```

## Поддержка

- Проблемы? Проверьте [README.md](README.md)
- Вопросы по Google Drive API? См. [GDRIVE_SETUP.md](GDRIVE_SETUP.md)
