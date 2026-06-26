# Use Node.js LTS version
FROM node:lts

# Set working directory
WORKDIR /usr/src/app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy application source code
COPY . .

# Expose application port
EXPOSE 3000

# Define environment variables
ENV NODE_ENV=production

# Start the application
CMD [ "npm", "start" ]
