FROM node:20-alpine AS builder

# Accept API base URL at build time (required for NEXT_PUBLIC_* variables)
ARG NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}

WORKDIR /app

RUN npm install -g pnpm

COPY package.json pnpm-lock.yaml .npmrc ./
RUN pnpm install --frozen-lockfile

COPY . .

RUN npx next build

FROM node:20-alpine

WORKDIR /app

RUN npm install -g pnpm

COPY --from=builder /app/package.json ./
COPY --from=builder /app/pnpm-lock.yaml ./
COPY --from=builder /app/.npmrc ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next

RUN pnpm install --prod --frozen-lockfile

EXPOSE 3004

CMD ["npx", "next", "start", "-p", "3004"]
