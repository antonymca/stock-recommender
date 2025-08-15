FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Copy Prisma schema before npm install
COPY prisma ./prisma

# Install dependencies (this will run prisma generate)
RUN npm install

# Copy the rest of the application
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
