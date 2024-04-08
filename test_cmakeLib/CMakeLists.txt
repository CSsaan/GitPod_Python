cmake_minimum_required(VERSION 3.10)
project(MyLib)

# 添加共享库的源文件
file(GLOB SOURCES "src/*.cpp")
# set(SOURCES mylib.cpp)

# 添加头文件路径
include_directories(include)

# 生成共享库
add_library(mylib_shared SHARED ${SOURCES})
# 生成静态库
add_library(mylib_static STATIC ${SOURCES})

# # 生成可执行程序
# add_executable(use_mylib main.cpp)
# # 链接共享库
# target_link_libraries(use_mylib mylib_shared)

# 指定安装路径
install(TARGETS mylib_shared DESTINATION /usr/local/lib)
install(FILES mylib.h DESTINATION /usr/local/include)