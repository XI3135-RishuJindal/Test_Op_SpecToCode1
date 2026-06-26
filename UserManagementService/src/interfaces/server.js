const express = require('express');
const dotenv = require('dotenv');

// Initialize configuration
dotenv.config();

// Create Express app
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
to parse JSON bodies
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).send({ status: 'UP' });
});

// Start server
app.listen(PORT, () => {
  console.log(`User Management Service is running on port ${PORT}`);
});
