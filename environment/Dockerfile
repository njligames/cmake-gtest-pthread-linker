FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

#   # Copy project files
#   COPY . .
#   
#   # Configure and build
#   RUN cmake -S . -B build \
#       && cmake --build build
#   
#   # Run tests
#   CMD ["ctest", "--test-dir", "build", "--verbose"]

