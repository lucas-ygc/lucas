cmake_minimum_required(VERSION 3.16)
project(linux_course_hello C)
add_executable(hello main.c message.h)
target_compile_options(hello PRIVATE -Wall -Wextra -Werror)
