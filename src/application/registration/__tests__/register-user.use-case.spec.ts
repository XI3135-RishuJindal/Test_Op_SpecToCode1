import { Test, TestingModule } from '@nestjs/testing';
import { RegisterUserUseCase } from '../use-cases/register-user.use-case';
import { USER_REPOSITORY } from '../../../domain/ports/user-repository.port';
import { VERIFICATION_TOKEN_REPOSITORY } from '../../../domain/ports/verification-token-repository.port';
import { OUTBOX_EVENT_REPOSITORY } from '../../../domain/ports/outbox-event-repository.port';
import { PASSWORD_HASHER } from '../../../domain/ports/password-hasher.port';
import { TOKEN_GENERATOR } from '../../../domain/ports/token-generator.port';
import { NOTIFICATION_SENDER } from '../../../domain/ports/notification-sender.port';
import { User } from '../../../domain/entities/user.entity';
import { Email } from '../../../domain/value-objects/email.vo';
import { AccountStatus } from '../../../domain/enums/account-status.enum';

const mockUserRepo = {
  findByIdempotencyKey: jest.fn(),
  findByEmail: jest.fn(),
  save: jest.fn(),
  update: jest.fn(),
  findById: jest.fn(),
};

const mockTokenRepo = {
  save: jest.fn(),
  findByTokenHash: jest.fn(),
  findActiveByUserId: jest.fn(),
  update: jest.fn(),
};

const mockOutboxRepo = {
  save: jest.fn(),
  findUnpublished: jest.fn(),
  markPublished: jest.fn(),
};

const mockHasher = {
  hash: jest.fn().mockResolvedValue('$argon2id$hashed'),
  verify: jest.fn(),
};

const mockTokenGen = {
  generate: jest.fn().mockResolvedValue({ raw: 'raw-token', hash: 'sha256-hash' }),
};

const mockNotifier = {
  sendVerificationEmail: jest.fn().mockResolvedValue(undefined),
};

describe('RegisterUserUseCase', () => {
  let useCase: RegisterUserUseCase;

  beforeEach(async () => {
    jest.clearAllMocks();

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        RegisterUserUseCase,
        { provide: USER_REPOSITORY, useValue: mockUserRepo },
        { provide: VERIFICATION_TOKEN_REPOSITORY, useValue: mockTokenRepo },
        { provide: OUTBOX_EVENT_REPOSITORY, useValue: mockOutboxRepo },
        { provide: PASSWORD_HASHER, useValue: mockHasher },
        { provide: TOKEN_GENERATOR, useValue: mockTokenGen },
        { provide: NOTIFICATION_SENDER, useValue: mockNotifier },
      ],
    }).compile();

    useCase = module.get<RegisterUserUseCase>(RegisterUserUseCase);
  });

  it('registers a new user and returns generic message', async () => {
    mockUserRepo.findByIdempotencyKey.mockResolvedValue(null);
    mockUserRepo.findByEmail.mockResolvedValue(null);
    mockUserRepo.save.mockImplementation((user: User) => Promise.resolve(user));
    mockTokenRepo.save.mockImplementation((t: any) => Promise.resolve(t));
    mockOutboxRepo.save.mockImplementation((e: any) => Promise.resolve(e));

    const result = await useCase.execute({
      email: 'alice@example.com',
      password: 'P@ssw0rd!',
      idempotencyKey: 'idem-1',
    });

    expect(result.message).toContain('verification');
    expect(mockHasher.hash).toHaveBeenCalledWith('P@ssw0rd!');
    expect(mockTokenGen.generate).toHaveBeenCalled();
    expect(mockNotifier.sendVerificationEmail).toHaveBeenCalledWith(
      'alice@example.com',
      'raw-token',
    );
  });

  it('returns generic message when email already exists (enumeration safety)', async () => {
    mockUserRepo.findByIdempotencyKey.mockResolvedValue(null);
    const existingUser = User.create({
      id: 'existing-id',
      email: new Email('alice@example.com'),
      passwordHash: 'hash',
      status: AccountStatus.ACTIVE,
      idempotencyKey: 'old-key',
    });
    mockUserRepo.findByEmail.mockResolvedValue(existingUser);

    const result = await useCase.execute({
      email: 'alice@example.com',
      password: 'P@ssw0rd!',
      idempotencyKey: 'idem-2',
    });

    expect(result.message).toBeDefined();
    expect(mockUserRepo.save).not.toHaveBeenCalled();
  });

  it('returns generic message on idempotent replay', async () => {
    const existingUser = User.create({
      id: 'existing-id',
      email: new Email('alice@example.com'),
      passwordHash: 'hash',
      status: AccountStatus.PENDING_VERIFICATION,
      idempotencyKey: 'idem-3',
    });
    mockUserRepo.findByIdempotencyKey.mockResolvedValue(existingUser);

    const result = await useCase.execute({
      email: 'alice@example.com',
      password: 'P@ssw0rd!',
      idempotencyKey: 'idem-3',
    });

    expect(result.message).toBeDefined();
    expect(mockUserRepo.save).not.toHaveBeenCalled();
  });

  it('throws on invalid email format', async () => {
    mockUserRepo.findByIdempotencyKey.mockResolvedValue(null);

    await expect(
      useCase.execute({
        email: 'not-an-email',
        password: 'P@ssw0rd!',
        idempotencyKey: 'idem-4',
      }),
    ).rejects.toThrow();
  });

  it('throws on weak password', async () => {
    mockUserRepo.findByIdempotencyKey.mockResolvedValue(null);

    await expect(
      useCase.execute({
        email: 'alice@example.com',
        password: 'weak',
        idempotencyKey: 'idem-5',
      }),
    ).rejects.toThrow();
  });
});
