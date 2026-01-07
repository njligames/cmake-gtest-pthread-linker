cat <<'EOF' > main.cpp
#include <boost/asio.hpp>
#include <boost/asio/ssl.hpp>
#include <boost/asio/ssl/host_name_verification.hpp>
#include <openssl/ssl.h>
#include <iostream>
#include <string>

using boost::asio::ip::tcp;

int main() {
    try {
        boost::asio::io_context io;
        boost::asio::ssl::context ctx(boost::asio::ssl::context::tls_client);

        ctx.set_default_verify_paths();
        ctx.set_options(
            boost::asio::ssl::context::default_workarounds |
            boost::asio::ssl::context::no_sslv2 |
            boost::asio::ssl::context::no_sslv3 |
            boost::asio::ssl::context::no_tlsv1 |
            boost::asio::ssl::context::no_tlsv1_1
        );

        boost::asio::ssl::stream<tcp::socket> socket(io, ctx);

        // REQUIRED: certificate + hostname verification
        socket.set_verify_mode(boost::asio::ssl::verify_peer);
        socket.set_verify_callback(
            boost::asio::ssl::host_name_verification("example.com")
        );

        // REQUIRED: set SNI (this is what was missing)
        if (!SSL_set_tlsext_host_name(socket.native_handle(), "example.com")) {
            throw std::runtime_error("Failed to set SNI hostname");
        }

        tcp::resolver resolver(io);
        auto endpoints = resolver.resolve("example.com", "443");
        boost::asio::connect(socket.lowest_layer(), endpoints);

        socket.handshake(boost::asio::ssl::stream_base::client);

        std::string request =
            "GET / HTTP/1.1\r\n"
            "Host: example.com\r\n"
            "Connection: close\r\n\r\n";

        boost::asio::write(socket, boost::asio::buffer(request));

        boost::asio::streambuf response;
        boost::asio::read_until(socket, response, "\r\n");

        std::istream response_stream(&response);
        std::string http_version;
        unsigned int status_code;

        response_stream >> http_version >> status_code;

        std::cout << status_code << std::endl;
    }
    catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}

EOF

cat <<'EOF' > CMakeLists.txt
cmake_minimum_required(VERSION 3.16)
project(main LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Boost (Asio depends on boost::system)
find_package(Boost REQUIRED COMPONENTS system)

# OpenSSL (required for TLS)
find_package(OpenSSL REQUIRED)

add_executable(main
    main.cpp
)

target_include_directories(main PRIVATE
    ${Boost_INCLUDE_DIRS}
)

target_link_libraries(main PRIVATE
    Boost::system
    OpenSSL::SSL
    OpenSSL::Crypto
)
EOF
