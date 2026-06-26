'use strict';

const request = require('supertest');

// Use mock notification service for all OTP tests
process.env.NODE_ENV = 'test';

const app = require('../../src/app');

describe('POST /api/v1/otp/generate', () => {
  it('should return 201 with otpId and expiresAt', async () => {
    const res = await request(app)
      .post('/api/v1/otp/generate')
      .send({ userId: 'user-001', phoneNumber: '+15005550006' });

    expect(res.statusCode).toBe(201);
    expect(res.body.otpId).toBeDefined();
    expect(res.body.expiresAt).toBeDefined();
  });

  it('should return 400 when userId is missing', async () => {
    const res = await request(app)
      .post('/api/v1/otp/generate')
      .send({ phoneNumber: '+15005550006' });

    expect(res.statusCode).toBe(400);
    expect(res.body.error).toBeDefined();
  });

  it('should return 400 when phoneNumber is missing', async () => {
    const res = await request(app)
      .post('/api/v1/otp/generate')
      .send({ userId: 'user-001' });

    expect(res.statusCode).toBe(400);
    expect(res.body.error).toBeDefined();
  });
});

describe('POST /api/v1/otp/validate', () => {
  it('should return valid: false for a non-existent OTP', async () => {
    const res = await request(app)
      .post('/api/v1/otp/validate')
      .send({ userId: 'user-999', code: '123456' });

    expect(res.statusCode).toBe(200);
    expect(res.body.valid).toBe(false);
  });

  it('should return valid: false for an incorrect code', async () => {
    // First generate an OTP
    await request(app)
      .post('/api/v1/otp/generate')
      .send({ userId: 'user-002', phoneNumber: '+15005550006' });

    // Then validate with wrong code
    const res = await request(app)
      .post('/api/v1/otp/validate')
      .send({ userId: 'user-002', code: '000000' });

    expect(res.statusCode).toBe(200);
    expect(res.body.valid).toBe(false);
  });

  it('should return 400 when userId is missing', async () => {
    const res = await request(app)
      .post('/api/v1/otp/validate')
      .send({ code: '123456' });

    expect(res.statusCode).toBe(400);
  });

  it('should return 400 when code is missing', async () => {
    const res = await request(app)
      .post('/api/v1/otp/validate')
      .send({ userId: 'user-001' });

    expect(res.statusCode).toBe(400);
  });
});
