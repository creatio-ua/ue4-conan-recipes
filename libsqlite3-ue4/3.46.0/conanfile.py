# from conans import ConanFile, CMake, tools
from conans import ConanFile, CMake, tools
import os
import re

class libSqlite3Ue4Conan(ConanFile):
    name = "libsqlite3-ue4"
    version = "3.46.0"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/adamrehn/ue4-conan-recipes/libsqlite3-ue4"
    description = "libSqlite3 custom build for Unreal Engine"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"
    requires = (
        "cmake/3.24.2"
        )


    def source(self):
        self.run(f"git clone --branch v{self.version} --single-branch --progress --depth=1 https://github.com/creatio-ua/libsqlite3.git")
        
        # Uncomment if CMake variables need to have non-default values
        #tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        #tc.variables["SQLITE_ENABLE_COLUMN_METADATA"] = self.options.enable_column_metadata
        #tc.variables["SQLITE_ENABLE_JSON1"] = self.options.enable_json1
        #tc.variables["SQLITE_ENABLE_RTCC"] = self.options.enable_rtcc
 
    def replace_with_re(self, filePath, pattern, replacement):
        # Ensure the file exists
        if not os.path.exists(filePath):
            raise FileNotFoundError(f"{filePath} not found!")

        # Read and modify the file content using regex
        with open(filePath, "r", encoding="utf-8") as file:
            content = file.read()

        # Replace the pattern in the content
        new_content = re.sub(pattern, replacement, content)

        # Write the modified content back to the file
        with open(filePath, "w", encoding="utf-8") as file:
            file.write(new_content)


    def build(self):
        #tools.replace_in_file("libsqlite3/CMakeLists.txt", 
        self.replace_with_re("libsqlite3/CMakeLists.txt", 
            re.compile(r"# Linking\s*target_link_libraries\(sqlite3\)", re.IGNORECASE),
                        """
add_executable(sqlite sqlite3.c shell.c sqlite3.h sqlite3ext.h)

add_definitions(-DSQLITE_ENABLE_RTREE)
add_definitions(-DSQLITE_ENABLE_FTS4)
add_definitions(-DSQLITE_ENABLE_FTS5)
add_definitions(-DSQLITE_ENABLE_JSON1)
add_definitions(-DSQLITE_ENABLE_RBU)
add_definitions(-DSQLITE_ENABLE_STAT4)

# Uncomment this for single-threaded variant (faster)
#add_definitions(-DSQLITE_THREADSAFE=0)

if(WIN32)
  add_custom_command(TARGET sqlite POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:sqlite> ${CMAKE_BINARY_DIR}/sqlite3.exe
    DEPENDS sqlite
  )
  install(FILES ${CMAKE_BINARY_DIR}/sqlite3.exe DESTINATION bin)
else()
  include(FindThreads)
  target_link_libraries(sqlite m ${CMAKE_THREAD_LIBS_INIT} ${CMAKE_DL_LIBS})
  install(TARGETS sqlite RUNTIME DESTINATION bin)
endif()

if (MSVC)
    add_compile_options(/wd4711) # Suppress C4711 warning
endif()
                        
file(GLOB HEADERS "*.h")
install(TARGETS sqlite3 ARCHIVE DESTINATION lib LIBRARY DESTINATION lib RUNTIME DESTINATION bin)
install(FILES ${HEADERS} DESTINATION include)

# Linking
target_link_libraries(sqlite3)
""")

        cmake = CMake(self)
        
        # Uncomment if CMake variables need to have non-default values
        # cmake.configure(source_folder="libsqlite3", args=self.cmake_flags())
        cmake.configure(source_folder="libsqlite3")
        cmake.build()


    def package(self):
        cmake = CMake(self)
        cmake.install()
        
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)