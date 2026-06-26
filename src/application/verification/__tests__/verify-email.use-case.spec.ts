import { Test, TestingModule } from '@nestjs/testing';
import { VerifyEmailUseCase } from '../use-cases/verify-email.use-case';
import { USER_REPOSITORY } from '../../../domain/ports/user-repository.port';
import { VERIFICATION_TOKEN_REPOSITORY } from '../../../domain/ports/verification-token-repository.port';
import { OUTBOX_EVENT_REPOSITORY } from '../../../domain/ports/outbox-event-repository.port';
import { VerificationToken } from '../../../domain/entities/verification-token.entity';
import { User } from '../../../domain/entities/user.entity';
import { Email } from '../../../domain/value-objects/email.vo';
import { AccountStatus } from '../../../domain/enums/account-status.enum';
import { createHash } from 'crypto';
import {
  InvalidVerificationTokenException,
  AccountNotPendingVerificationException,
} from '../../../domain/exceptions/domain.exceptions';

const mockUserRepo = {
  findById: jest.fn(),
  findByEmail: jest.fn(),
  findByIdempotencyKey: jest.fn(),
  save: jest.fn(),
  update: jest.fn(),
};

const mockTokenRepo = {
  findByTokenHash: jest.fn(),
  findActiveByUserId: jest.fn(),
  save: jest.fn(),
  update: jest.fn(),
};

const mockOutboxRepo = {
  save: jest.fn(),
  findUnpublished: jest.fn(),
  markPublished: jest.fn(),
};

describe('VerifyEmailUseCase', () => {
  let useCase: VerifyEmailUseCase;

  const RAW_TOKEN = 'raw-token-abc123';
  const TOKEN_HASH = createHash('sha256').update(RAW_TOKEN).digest('hex');

  const pendingUser = User.create({
    id: 'user-1',
    email: new Email('alice@example.com'),
    passwordHash: '$argon2id$...',
    status: AccountStatus.PENDING_VERIFICATION,
    idempotencyKey: 'idem-1',
  });

  const validToken = VerificationToken.create({
    id: 'tok-1',
    userId: 'user-1',
    tokenHash: TOKEN_HASH,
    expiresAt: new Date(Date.now() + 60 * 60 * 1000),
  });

  beforeEach(async () => {
    jest.clearAllMocks();

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        VerifyEmailUseCase,
        { provide: USER_REPOSITORY, useValue: mockUserRepo },
        { provide: VERIFICATION_TOKEN_REPOSITORY, useValue: mockTokenRepo },
        { provide: OUTBOX_EVENT_REPOSITORY, useValue: mockOutboxRepo },
      ],
    }).compile();

    useCase = module.get<VerifyEmailUseCase>(VerifyEmailUseCase);
  });

  it('verifies email and activates user', async () => {
    mockTokenRepo.findByTokenHash.mockResolvedValue(validToken);
    mockUserRepo.findById.mockResolvedValue(pendingUser);
    mockUserRepo.update.mockImplementation((u: User) => Promise.resolve(u));
    mockTokenRepo.update.mockImplementation((t: VerificationToken) => Promise.resolve(t));
    mockOutboxRepo.save.mockImplementation((e: any) => Promise.resolve(e));

    const result = await useCase.execute({ token: RAW_TOKEN });

    expect(result.message).toBeDefined();
    expect(mockUserRepo.update).toHaveBeenCalled();
    expect(mockTokenRepo.update).toHaveBeenCalled();
    expect(mockOutboxRepo.save).toHaveBeenCalled();
  });

  it('throws InvalidVerificationTokenException for unknown token', async () => {
    mockTokenRepo.findByTokenHash.mockResolvedValue(null);

    await expect(useCase.execute({ token: 'unknown-token' })).rejects.toThrow(
      InvalidVerificationTokenException,
    );
  });

  it('throws InvalidVerificationTokenException for expired token', async () => {
    const expiredToken = VerificationToken.create({
      id: 'tok-exp',
      userId: 'user-1',
      tokenHash: TOKEN_HASH,
      expiresAt: new Date(Date.now() - 1000),
    });
    mockTokenRepo.findByTokenHash.mockResolvedValue(expiredToken);

    await expect(useCase.execute({ token: RAW_TOKEN })).rejects.toThrow(
      InvalidVerificationTokenException,
    );
  });

  it('throws AccountNotPendingVerificationException for already-active user', async () => {
    const activeUser = User.reconstitute({
      id: 'user-1',
      email: new Email('alice@example.com'),
      passwordHash: '$argon2id$...',
      status: AccountStatus.ACTIVE,
      idempotencyKey: 'idem-1',
      createdAt: new Date(),
      updatedAt: new Date(),
    });
    mockTokenRepo.findByTokenHash.mockResolvedValue(validToken);
    mockUserRepo.findById.mockResolvedValue(activeUser);

    await expect(useCase.execute({ token: RAW_TOKEN })).rejects.toThrow(
      AccountNotPendingVerificationException,
    );
  });
});
