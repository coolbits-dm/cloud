# Dockerfile for User Panel
FROM node:20-alpine

ENV NODE_ENV=production
ENV PANEL_TYPE=user
ENV PANEL_TOKENS=1000

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Start the application
CMD ["node", "app.js"]
