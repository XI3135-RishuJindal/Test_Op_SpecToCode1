import { Kafka, Producer, logLevel } from 'kafkajs';
import { config } from '../config';
import { logger } from './logger';

let producer: Producer | null = null;

const kafka = new Kafka({
  clientId: config.kafka.clientId,
  brokers: config.kafka.brokers,
  logLevel: logLevel.WARN,
  retry: {
    initialRetryTime: 300,
    retries: 8,
  },
});

export async function getProducer(): Promise<Producer> {
  if (!producer) {
    producer = kafka.producer({
      allowAutoTopicCreation: true,
      transactionTimeout: 30_000,
    });
    await producer.connect();
    logger.info('Kafka producer connected');
  }
  return producer;
}

export async function publishMessage(
  topic: string,
  key: string,
  value: unknown,
): Promise<void> {
  try {
    const p = await getProducer();
    await p.send({
      topic,
      messages: [
        {
          key,
          value: JSON.stringify(value),
          timestamp: Date.now().toString(),
        },
      ],
    });
  } catch (err) {
    logger.error({ err, topic, key }, 'Failed to publish Kafka message');
    // Do NOT propagate — audit publish failure must not fail the request
  }
}

export async function disconnectKafka(): Promise<void> {
  if (producer) {
    await producer.disconnect();
    producer = null;
  }
}
