# Frontend — Next.js standalone
#
# NEXT_PUBLIC_* được nhúng thẳng vào bundle lúc BUILD, không đọc lúc chạy.
# Nghĩa là đổi địa chỉ API thì phải build lại image, không sửa env rồi restart
# được. Vì thế nó là build arg chứ không phải biến môi trường runtime.

FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci


FROM node:22-alpine AS builder
WORKDIR /app

ARG NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_TELEMETRY_DISABLED=1

COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build


FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

RUN addgroup -g 10001 -S nodejs && adduser -u 10001 -S nextjs -G nodejs

# standalone gói sẵn server.js và node_modules tối thiểu; static và public
# phải copy riêng vì Next không nhét chúng vào standalone.
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs
EXPOSE 3000

CMD ["node", "server.js"]
