# syntax=docker/dockerfile:1

FROM node:20
WORKDIR /python-check-weather/
COPY . .
RUN yarn install --production
CMD ["node", "src/index.js"]
EXPOSE 3000
