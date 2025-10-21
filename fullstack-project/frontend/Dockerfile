# /frontend/Dockerfile
# Stage 1: Build the Next.js application
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve the application
FROM node:20-alpine AS runner
WORKDIR /app
# Copy only the necessary files from the builder stage
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Expose the port (Next.js default is 3000)
EXPOSE 3000

# Set Next.js to run in production mode
ENV NODE_ENV production

# Start the Next.js application
CMD ["npm", "start"]