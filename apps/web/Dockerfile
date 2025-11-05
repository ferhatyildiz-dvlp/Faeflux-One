FROM node:20-alpine

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Set working directory
WORKDIR /app

# Copy package files first
COPY package.json ./

# Copy lockfile if it exists, otherwise just continue
COPY pnpm-lock.yaml* ./

# Install dependencies (lockfile varsa frozen, yoksa normal install)
RUN pnpm install || pnpm install --no-frozen-lockfile

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Development command (for docker-compose)
CMD ["pnpm", "dev"]

