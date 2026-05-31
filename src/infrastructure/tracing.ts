import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { JaegerExporter } from '@opentelemetry/exporter-jaeger';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { config } from '../config';
import { logger } from './logger';

let sdk: NodeSDK | null = null;

export function initTracing(): void {
  try {
    const exporter = new JaegerExporter({
      endpoint: config.observability.jaegerEndpoint,
    });

    sdk = new NodeSDK({
      resource: new Resource({
        [SemanticResourceAttributes.SERVICE_NAME]: config.service.name,
        [SemanticResourceAttributes.SERVICE_VERSION]: config.service.version,
        [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: config.env,
      }),
      traceExporter: exporter,
      instrumentations: [getNodeAutoInstrumentations()],
    });

    sdk.start();
    logger.info('OpenTelemetry tracing initialized');
  } catch (err) {
    logger.warn({ err }, 'Failed to initialize tracing — continuing without tracing');
  }
}

export async function shutdownTracing(): Promise<void> {
  if (sdk) {
    await sdk.shutdown();
  }
}
