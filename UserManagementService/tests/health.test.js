const request = require('supertest');
const express = require('express');

const app = express();

// Health check endpoint
describe('GET /health', () => {
  it('should return 200 and status UP', async () => {
    app.get('/health', (req, res) => {
      res.status(200).send({ status: 'UP' });
    });

    const response = await request(app).get('/health');
    expect(response.statusCode).toBe(200);
    expect(response.body).toEqual({ status: 'UP' });
  });
});
