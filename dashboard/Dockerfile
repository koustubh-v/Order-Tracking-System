FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

# Build the react app (or we can run vite in dev mode)
# Standard for development/demo is dev server to allow easy proxying/env vars
CMD ["npm", "run", "dev", "--", "--host"]
