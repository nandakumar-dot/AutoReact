# Use a Node.js base image
FROM node:16-alpine

# Set the working directory to /app
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json ./
RUN npm install

# Copy generated files and start React app
COPY ./generated ./generated
EXPOSE 3000
CMD ["npm", "start"]
