# syntax=docker/dockerfile:1

FROM node:21
WORKDIR /python-check-weather/
COPY . .
RUN yarn install --production
CMD ["node", "src/index.js"]
EXPOSE 8000
