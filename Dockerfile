FROM node:22-alpine AS development
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts --no-audit --no-fund
COPY tools ./tools
COPY site ./site
COPY content ./content
COPY static ./static
ENV HOST=0.0.0.0
EXPOSE 4000
CMD ["npm", "run", "dev"]

FROM development AS build
RUN npm run build

FROM nginx:stable-alpine AS production
COPY docker/lucas.nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
