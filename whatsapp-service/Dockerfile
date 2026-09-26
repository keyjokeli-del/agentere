# ==============================================================================
# STAGE 1: Install Production Dependencies
# ==============================================================================
FROM node:20-alpine AS builder

WORKDIR /build

COPY package*.json ./
RUN npm ci --omit=dev --no-audit --no-fund && npm cache clean --force

# ==============================================================================
# STAGE 2: RAM-Optimized Production Runtime (Baileys + Neon DB)
# ==============================================================================
FROM node:20-alpine AS runner

WORKDIR /app

# Production and Memory Capping Flags:
# - NODE_ENV=production enables performance optimizations in express/pg
# - NODE_OPTIONS="--max-old-space-size=256" restricts V8 heap to 256MB to avoid OOM in 512MB RAM tier
ENV NODE_ENV=production \
    NODE_OPTIONS="--max-old-space-size=256" \
    PORT=3001

# Copy production node_modules from builder stage
COPY --from=builder /build/node_modules ./node_modules
COPY --chown=node:node package*.json ./
COPY --chown=node:node index.js ./
COPY --chown=node:node neonAuthState.js ./

# Create directory for fallback auth and assign permissions to built-in 'node' user
RUN mkdir -p /app/auth_info_baileys && chown -R node:node /app

USER node

EXPOSE 3001

# Health check using native Node.js HTTP to avoid external curl dependencies
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD node -e "require('http').get('http://localhost:' + (process.env.PORT || 3001) + '/api/status', (res) => { if (res.statusCode !== 200) process.exit(1); })"

CMD ["node", "index.js"]
