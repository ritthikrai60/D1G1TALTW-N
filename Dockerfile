# Stage 1: Build Frontend
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Production Server + Network Scanner Tools
FROM node:22-alpine
WORKDIR /app

# Install network discovery utilities (ping, arp/net-tools, iproute2, nmap)
RUN apk add --no-cache iputils net-tools iproute2 nmap

COPY package*.json ./
RUN npm install --omit=dev

COPY --from=builder /app/dist ./dist
COPY server ./server
COPY public ./public

# Create persistent data directory
RUN mkdir -p /app/data

ENV NODE_ENV=production
ENV PORT=8085
ENV ADMIN_PASSWORD=admin123

EXPOSE 8085

CMD ["node", "server/index.js"]

