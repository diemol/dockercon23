FROM node:18-alpine
WORKDIR /app
COPY app/package.json app/package-lock.json /app/
RUN npm install --production
EXPOSE 3000
CMD ["node", "/app/src/index.js"]
COPY app .
