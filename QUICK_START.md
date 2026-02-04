# Quick Start - Document Summarizer

## ⚠️ ВАЖНО: Рабочий метод

**Используйте [`summarize_download.py`](summarize_download.py:1)** - это правильный подход:
1. ✅ Скачивает файлы с Google Drive
2. ✅ Извлекает текст локально
3. ✅ Отправляет текст в LLM для суммаризации

## Быстрый старт

### Шаг 1: Получить File IDs

Откройте папку в браузере и извлеките File IDs:

```
https://drive.google.com/drive/folders/1x6EKNkVw6PlFVTr6cGrsVscmRuwqGrXd
```

Для каждого файла:
1. Кликните на файл
2. Скопируйте ID из URL: `https://drive.google.com/file/d/FILE_ID/view`

Пример: `https://drive.google.com/file/d/1abc123XYZ456def/view` → ID: `1abc123XYZ456def`

### Шаг 2: Создать file_ids.txt

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

1. Регистрация (бесплатно): https://openrouter.ai/
2. Получите API ключ
3. Установите:

```bash
export OPENROUTER_API_KEY=your_key_here
```

### Шаг 5: Запустить

```bash
# Из файла с IDs
python summarize_download.py --file-list file_ids.txt

# Или напрямую с IDs
python summarize_download.py --file-ids ID1 ID2 ID3

# С пользовательскими параметрами
python summarize_download.py \
    --file-list file_ids.txt \
    --model google/gemma-2-9b-it:free \
    --output my_summary.json
```

## Результат

```
============================================================
GOOGLE DRIVE DOCUMENT SUMMARIZER
(Download + Parse + Summarize)
============================================================

Processing 3 files...
Model: google/gemma-2-9b-it:free

Temporary directory: /tmp/tmpXXXXXX

============================================================
DOWNLOADING AND PARSING FILES
============================================================

[1/3] Processing: 1abc123XYZ456def
  ✓ Parsed as .pdf: 5432 characters
[2/3] Processing: 2xyz789ABC012ghi
  ✓ Parsed as .docx: 3210 characters
[3/3] Processing: 3mno345PQR678stu
  ✓ Parsed as text: 1234 characters

============================================================
GENERATING SUMMARIES
============================================================

[1/3] Summarizing: document_1.pdf
  ✓ Summary generated
  Preview: This document discusses...

[2/3] Summarizing: document_2.docx
  ✓ Summary generated
  Preview: The main topics include...

[3/3] Summarizing: document_3.txt
  ✓ Summary generated
  Preview: Key points are...

============================================================
GENERATING MASTER SUMMARY
============================================================

============================================================
SUMMARY STATISTICS
============================================================
Total Documents: 3
Successful: 3
Failed: 0
Total Size: 9,876 bytes

============================================================
MASTER SUMMARY
============================================================

This collection of documents covers:
1. [Тема 1] - основная информация...
2. [Тема 2] - детали о...
3. [Тема 3] - анализ...

В целом, документы предоставляют комплексное описание...

============================================================

✓ Cleaned up temporary files
✓ Full report saved to: summary_report.json
✓ Complete!
```

## Структура JSON отчета

```json
{
  "master_summary": "Общий обзор всех документов...",
  "statistics": {
    "total_documents": 3,
    "successful_summaries": 3,
    "failed_summaries": 0,
    "total_size_bytes": 9876,
    "file_types": {
      ".pdf": 1,
      ".docx": 1,
      ".txt": 1
    }
  },
  "individual_summaries": [
    {
      "filename": "document_1.pdf",
      "file_id": "1abc123XYZ456def",
      "type": ".pdf",
      "size": 5432,
      "content": "Полный текст документа...",
      "summary": "Краткое содержание...",
      "summary_status": "success"
    }
  ],
  "metadata": {
    "generated_at": "2026-02-04T09:33:00",
    "model_used": "google/gemma-2-9b-it:free",
    "total_files": 3,
    "method": "download_and_parse"
  }
}
```

## Доступные модели (бесплатные)

```bash
# Gemma (хорошее качество)
--model google/gemma-2-9b-it:free

# Gemini Flash (быстрая)
--model google/gemini-flash-1.5:free

# Llama (альтернатива)
--model meta-llama/llama-3.2-3b-instruct:free

# Qwen (еще одна опция)
--model qwen/qwen-2-7b-instruct:free
```

## Troubleshooting

### "Download error"
- Убедитесь что файлы публичные (Anyone with the link can view)
- Проверьте правильность File IDs

### "Parse error"
- Установите все библиотеки: `pip install -r requirements.txt`
- Поддерживаемые форматы: PDF, DOCX, TXT, HTML, XLSX, RTF, MD, CSV

### "API Error: 502"
- ✅ **Эта проблема решена в `summarize_download.py`**
- Старый `summarize_public.py` не работал, так как модели не могут читать файлы напрямую по URL
- Новый подход скачивает файлы и извлекает текст локально

### "Rate limit exceeded"
- Подождите несколько секунд между запросами
- Попробуйте другую бесплатную модель

## Пример для практической задачи

Для папки: `https://drive.google.com/drive/folders/1x6EKNkVw6PlFVTr6cGrsVscmRuwqGrXd`

1. Откройте папку, извлеките все File IDs
2. Создайте `task_file_ids.txt`:
```
<список ваших file IDs, один на строку>
```

3. Запустите:
```bash
export OPENROUTER_API_KEY=your_key_here
python summarize_download.py --file-list task_file_ids.txt --output task_summary.json
```

4. Результат будет в `task_summary.json` - это и есть ваш саммари!

## Почему этот метод работает?

**Проблема с прямыми URL:**
- Модели OpenRouter НЕ могут читать файлы напрямую из Google Drive
- Ошибка `502 Bad Gateway` означает, что провайдер не может обработать URL

**Решение - Download + Parse + Summarize:**
1. ✅ Скачиваем файлы во временную папку
2. ✅ Извлекаем текст с помощью специализированных библиотек (PyPDF2, python-docx, и т.д.)
3. ✅ Отправляем чистый текст в LLM
4. ✅ Получаем качественные саммари
5. ✅ Удаляем временные файлы

Этот подход **надежный и универсальный**!
