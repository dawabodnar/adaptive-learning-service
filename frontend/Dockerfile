# ─────────────────────────────────────────────────────────────────────────────
# frontend/Dockerfile
# Контейнер для клієнтської частини: React 19 + Vite.
# Multi-stage build: спочатку збираємо бандл, потім подаємо через Nginx.
# Розміщення: frontend/Dockerfile
# ─────────────────────────────────────────────────────────────────────────────

# ─── Етап 1: збірка продакшен-бандлу ────────────────────────────────────────
FROM node:22 AS build

WORKDIR /app

# Спочатку — package.json (краще кешування шару npm install)
COPY package*.json ./
RUN npm ci

# Тепер — увесь код фронтенду
COPY . .

# Збираємо оптимізований продакшен-бандл у /app/dist
RUN npm run build


# ─── Етап 2: подавання статичних файлів через Nginx ─────────────────────────
FROM nginx:1.27

# Видаляємо дефолтну конфігурацію та підставляємо нашу
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Копіюємо зібраний бандл з першого етапу
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]