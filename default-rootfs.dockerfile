FROM alpine:latest

RUN apk add --no-cache python3 bash curl wget py3-numpy py3-pandas py3-httpx py3-requests py3-pillow imagemagick
RUN adduser -D sandbox
USER sandbox