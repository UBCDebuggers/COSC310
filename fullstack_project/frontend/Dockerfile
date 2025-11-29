# ---------- Stage 1: Build ----------
FROM node:20-bookworm AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# ---------- Stage 2: Run ----------
FROM node:20-bookworm AS runner
WORKDIR /app

ENV NODE_ENV=production

# Copy only what runtime needs
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.mjs ./next.config.mjs

EXPOSE 3000
CMD ["npm", "start"]
