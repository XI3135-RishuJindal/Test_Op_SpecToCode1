'use strict';

const request = require('supertest');
const app = require('../../src/app');

describe('GET /health', () => {
  it('should return 200 with status ok', async () => {
    const res = await request(app).get('/health');

    expect(res.statusCode).toBe(200);
    expect(res.body).toMatchObject({
      status: 'ok',
      service: 'multi-factor-authentication-service',
    });
    expect(res.body.timestamp).toBeDefined();
  });

  it('should return a valid ISO 8601 timestamp', async () => {
    const res = await request(app).get('/health');

    const ts = new Date(res.body.timestamp);
    expect(ts.toString()).not.toBe('Invalid Date');
  });

  it('should respond with Content-Type application/json', async () => {
    const res = await request(app).get('/health');

    expect(res.headers['content-type']).toMatch(/application\/json/);
  });
});
