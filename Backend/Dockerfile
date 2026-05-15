FROM golang:1.21-alpine AS builder

WORKDIR /app

COPY . .

RUN go mod tidy && \
    CGO_ENABLED=0 GOOS=linux go build -o /server .

FROM alpine:3.18

RUN apk add --no-cache ca-certificates tzdata

COPY --from=builder /server /server

EXPOSE 3333

CMD ["/server"]
