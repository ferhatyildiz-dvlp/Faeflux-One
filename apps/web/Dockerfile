FROM node:20-alpine

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json ./
COPY pnpm-lock.yaml* ./

# Install dependencies (use --no-frozen-lockfile if lockfile doesn't exist)
RUN if [ -f pnpm-lock.yaml ]; then \
        pnpm install --frozen-lockfile; \
    else \
        pnpm install; \
    fi

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Development command (for docker-compose)
CMD ["pnpm", "dev"]

# Production build (uncomment for production)
# RUN pnpm build
# CMD ["pnpm", "start"]

