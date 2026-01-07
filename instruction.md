# Configure cmake boost openssl https
A CMake-based C++ project using Boost.Asio and OpenSSL fails at link time due to missing SSL and crypto libraries. 
Update CMakeLists.txt (or build invocation) to correctly find and link OpenSSL and required Boost components, then 
verify the resulting HTTPS client connects to example.com and prints the HTTP status code.

