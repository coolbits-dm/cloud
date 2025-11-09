# Dockerfile for Andrei Panel (Godlike)
FROM node:20-alpine

ENV NODE_ENV=production
ENV PANEL_TYPE=andrei
ENV PANEL_POWER=godlike

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
