# Асинхронный сервис процессинга платежей

Микросервис принимает платежи, обрабатывает их через эмуляцию платёжного шлюза и уведомляет клиента через webhook. Используется Outbox pattern, RabbitMQ и Dead Letter Queue.

## Быстрый старт

```bash
cp .env.example .env
make up
```

Сервисы:
- API docs — http://localhost:8000/docs
- RabbitMQ Management — http://localhost:15672
- pgAdmin — http://localhost:8080

## Команды

```bash
make up           # сборка и старт
make logs         # логи api
make logs-worker  # логи воркера
make down         # остановка
```

## Примеры запросов

Создание платежа:

```bash
curl -s -X POST 'http://localhost:8000/api/v1/payments/' \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: test123456' \
  -H 'Idempotency-Key: test-key-001' \
  -d '{
    "amount": "100.50",
    "currency": "RUB",
    "description": "Test payment",
    "meta_data": {"order_id": "42"},
    "webhook_url": "https://webhook.site/your-uuid"
  }'
```

Получение платежа:

```bash
curl -s 'http://localhost:8000/api/v1/payments/<payment_id>' \
  -H 'X-API-Key: test123456'
```

## Архитектура кратко

1. `POST /api/v1/payments` создаёт платёж (`pending`) и запись в outbox в одной транзакции.
2. Outbox relay публикует событие в очередь `payments.new` (очередь объявляется и на стороне API).
3. Воркер эмулирует шлюз (2–5 сек, 90% success / 10% fail), сохраняет статус, затем отправляет webhook с 3 ретраями.
4. Сообщения, окончательно упавшие на webhook, попадают в `payments.dlq`.
