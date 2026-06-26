import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication, ValidationPipe } from '@nestjs/common';
import * as request from 'supertest';
import { TerminusModule } from '@nestjs/terminus';
import { HealthController } from '../src/interfaces/http/health/health.controller';
import { HealthCheckService, TypeOrmHealthIndicator } from '@nestjs/terminus';

/**
 * E2E test for the health endpoint.
 *
 * We mock the database indicator so this test runs without a real DB.
 */
describe('GET /health (e2e)', () => {
  let app: INestApplication;

  const mockHealthCheckService = {
    check: jest.fn().mockResolvedValue({
      status: 'ok',
      info: { database: { status: 'up' } },
      error: {},
      details: { database: { status: 'up' } },
    }),
  };

  const mockDbIndicator = {
    pingCheck: jest.fn().mockResolvedValue({ database: { status: 'up' } }),
  };

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [TerminusModule],
      controllers: [HealthController],
      providers: [
        { provide: HealthCheckService, useValue: mockHealthCheckService },
        { provide: TypeOrmHealthIndicator, useValue: mockDbIndicator },
      ],
    }).compile();

    app = moduleFixture.createNestApplication();
    app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }));
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it('should return 200 with status ok', async () => {
    const response = await request(app.getHttpServer()).get('/health').expect(200);

    expect(response.body).toMatchObject({
      status: 'ok',
      info: { database: { status: 'up' } },
    });
  });

  it('should include database info in the response', async () => {
    const response = await request(app.getHttpServer()).get('/health').expect(200);

    expect(response.body.info).toHaveProperty('database');
    expect(response.body.info.database.status).toBe('up');
  });
});
