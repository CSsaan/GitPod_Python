cmake_minimum_required(VERSION 3.10)
project(UseLib)

# 添加共享库的源文件
# file(GLOB SOURCES "src/*.cpp")
set(SOURCES use_lib.cpp)

# 添加头文件路径
include_directories(include)

# 生成可执行程序
add_executable(use_mylib use_lib.cpp)

# # # 链接lib文件夹里的共享库
set(LIB_DIR ${CMAKE_SOURCE_DIR}/lib)
target_link_libraries(use_mylib PUBLIC ${LIB_DIR}/libmylib_shared.so)

# # 查找共享库
# set(LIB_DIR ${CMAKE_SOURCE_DIR}/lib)
# find_library(LIBRARY_NAME NAMES mylib_shared mylib_static PATHS ${LIB_DIR})
# message(STATUS "LIBRARY_NAME: ${LIBRARY_NAME}")
# target_link_libraries(use_mylib ${LIBRARY_NAME})
