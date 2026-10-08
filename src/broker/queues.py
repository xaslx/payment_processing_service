from faststream.rabbit import RabbitQueue

dlq_queue = RabbitQueue(name="payments.dlq", durable=True)

main_queue = RabbitQueue(
    name="payments.new",
    durable=True,
    arguments={
        "x-dead-letter-exchange": "",
        "x-dead-letter-routing-key": "payments.dlq",
    },
)
