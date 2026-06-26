import { Test, TestingModule } from '@nestjs/testing';
import { HealthController } from '../../interfaces/http/health/health.controller';
import { HealthCheckService, TypeOrmHealthIndicator } from '@nestjs/terminus';

describe('HealthController', () => {
  let controller: HealthController;
  let healthCheckService: jest.Mocked<HealthCheckService>;
  let dbIndicator: jest.Mocked<TypeOrmHealthIndicator>;

  beforeEach(async () => {
    const mockHealthCheckService = {
      check: jest.fn(),
    };
    const mockDbIndicator = {
      pingCheck: jest.fn(),
    };

    const module: TestingModule = await Test.createTestingModule({
      controllers: [HealthController],
      providers: [
        { provide: HealthCheckService, useValue: mockHealthCheckService },
        { provide: TypeOrmHealthIndicator, useValue: mockDbIndicator },
      ],
    }).compile();

    controller = module.get<HealthController>(HealthController);
    healthCheckService = module.get(HealthCheckService);
    dbIndicator = module.get(TypeOrmHealthIndicator);
  });

  it('should be defined', () => {
    expect(controller).toBeDefined();
  });

  it('should call health.check() and return its result', async () => {
    const mockResult = {
      status: 'ok',
      info: { database: { status: 'up' } },
      error: {},
      details: { database: { status: 'up' } },
    };

    dbIndicator.pingCheck.mockResolvedValue({ database: { status: 'up' } });
    healthCheckService.check.mockResolvedValue(mockResult as any);

    const result = await controller.check();
    expect(result).toEqual(mockResult);
    expect(healthCheckService.check).toHaveBeenCalledTimes(1);
  });

  it('should propagate errors from health.check()', async () => {
    healthCheckService.check.mockRejectedValue(new Error('DB unreachable'));
    await expect(controller.check()).rejects.toThrow('DB unreachable');
  });
});
