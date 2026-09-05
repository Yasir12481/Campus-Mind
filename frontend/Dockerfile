FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

ENV NEXT_PUBLIC_API_URL=http://localhost:8000
COPY . .
RUN npx next build --webpack

EXPOSE 3000
CMD ["npm", "start"]
