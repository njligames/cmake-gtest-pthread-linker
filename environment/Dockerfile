# Use Ubuntu 24.04 as base
FROM ubuntu:24.04

# Install build tools, Boost, OpenSSL, and CA certificates
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    libboost-system-dev \
    libboost-thread-dev \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app
