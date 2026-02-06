# Enterprise-ready Suno Automation Tool

*[Читать на русском языке (Read in Russian)](#suno-automation-tool-enterprise-ready-ru)*

This project represents a robust, production-grade automation interface for the Suno AI music generation platform. It is engineered to handle the full lifecycle of song creation with reliability, stealth, and scalability in mind.

## 🚀 Key Features

*   **Automated Generation**: Seamlessly constructs complex payloads for the `chirp-auk-turbo` model.
*   **Asynchronous Status Monitoring**: Implements intelligent polling with configurable timeouts to track generation status in real-time.
*   **Smart Error Handling**: Robust recovery mechanisms for network jitter, API errors, and malformed responses.
*   **Anti-Bot & Captcha Architecture**: A built-in, modular system designed to detect and resolve hCaptcha challenges automatically.

## 🏗️ Architecture & Stealth

To ensure longevity and resist automated bans, this tool implements advanced browser mimicry techniques:

1.  **Fingerprint Simulation**: The system injects precise `device-id` and `browser-token` headers to replicate a legitimate user session.
2.  **Request Signature**: All HTTP headers (including User-Agent and Client hints) are harmonized to match a standard Chrome/Windows environment.
3.  **UUID Rotation**: Every generation request generates a fresh `transaction_uuid` to maintain request uniqueness and avoid replay detection.

## 🛡️ Captcha Bypass System

The core `SunoAuto` class includes a dedicated interception layer for security challenges.

*   **Detection**: The `generate()` method inspects every API response for the `captcha_type` signal.
*   **Resolution**: The `_solve_captcha` method provides a pluggable interface for external solvers.
    *   *Ready Integration*: The code is pre-wired for **Capsolver** API integration.
    *   *Scalability*: Designed to support retry logic seamlessly—once a token is solved, the original request is automatically re-signed and resent.

## ⚙️ Setup & Deployment

### 1. Installation

Clone the repository and install the dependencies:

```bash
git clone <your-repo-url>
cd suno-automation
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
```

### 2. Configuration

Create your local configuration file from the template:

```powershell
cp .env.example .env
```

Edit `.env` and populate it with your session credentials:

```ini
SUNO_AUTH_TOKEN=your_jwt_access_token
SUNO_BROWSER_TOKEN={"token":"timestamp_token"}
SUNO_DEVICE_ID=your_device_uuid
CAPSOLVER_API_KEY=your_capsolver_key_optional
```

### 3. Usage

Run the testing script to validate the pipeline:

```powershell
python test_run.py
```

## ⚠️ Disclaimer

This tool is developed for **educational and testing purposes only**. It is not affiliated with Suno. Use responsibly and in accordance with the platform's Terms of Service.

---

# Suno Automation Tool (Enterprise-ready) [RU]

Этот проект представляет собой надежный интерфейс автоматизации промышленного уровня для платформы генерации музыки Suno AI. Он разработан для полного цикла управления созданием песен с упором на надежность, скрытность и масштабируемость.

## 🚀 Основные Возможности

*   **Автоматическая Генерация**: Формирование сложных payload-запросов для модели `chirp-auk-turbo`.
*   **Асинхронный Мониторинг**: Умный пулинг (polling) статуса с настраиваемыми таймаутами для отслеживания генерации в реальном времени.
*   **Умная Обработка Ошибок**: Механизмы восстановления при сетевых сбоях, ошибках API и некорректных ответах.
*   **Архитектура Анти-Бот и Обход Капчи**: Встроенная модульная система для автоматического обнаружения и решения задач hCaptcha.

## 🏗️ Архитектура и Скрытность

Для обеспечения долговечности работы и защиты от автоматических банов, инструмент использует продвинутые техники имитации браузера:

1.  **Симуляция Фингерпринтов**: Система внедряет точные заголовки `device-id` и `browser-token`, повторяя сессию легитимного пользователя.
2.  **Подпись Запросов**: Все HTTP-заголовки (включая User-Agent и Client hints) гармонизированы для соответствия стандартному окружению Chrome/Windows.
3.  **Ротация UUID**: Каждый запрос на генерацию создает новый `transaction_uuid` для обеспечения уникальности и предотвращения детектирования повторов.

## 🛡️ Система Обхода Капчи

В класс `SunoAuto` встроен специальный слой перехвата проверок безопасности.

*   **Обнаружение**: Метод `generate()` проверяет каждый ответ API на наличие сигнала `captcha_type`.
*   **Решение**: Метод `_solve_captcha` предоставляет подключаемый интерфейс для внешних решателей.
    *   *Готовая Интеграция*: Код уже подготовлен для работы с API **Capsolver**.
    *   *Масштабируемость*: Поддержка логики повторных попыток — как только токен капчи получен, оригинальный запрос автоматически подписывается заново и отправляется повторно.

## ⚙️ Установка и Развертывание

### 1. Установка

Клонируйте репозиторий и установите зависимости:

```bash
git clone <your-repo-url>
cd suno-automation
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
```

### 2. Конфигурация

Создайте локальный файл конфигурации из шаблона:

```powershell
cp .env.example .env
```

Отредактируйте `.env` и добавьте ваши учетные данные:

```ini
SUNO_AUTH_TOKEN=ваш_jwt_access_token
SUNO_BROWSER_TOKEN={"token":"timestamp_token"}
SUNO_DEVICE_ID=ваш_device_uuid
CAPSOLVER_API_KEY=ваш_capsolver_key_optional
```

### 3. Использование

Запустите тестовый скрипт для проверки пайплайна:

```powershell
python test_run.py
```

## ⚠️ Отказ от ответственности

Этот инструмент разработан исключительно в **образовательных и тестовых целях**. Он не аффилирован с Suno. Используйте его ответственно и в соответствии с Условиями использования платформы.
