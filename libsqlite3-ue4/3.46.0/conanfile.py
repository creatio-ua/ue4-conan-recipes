# from conans import ConanFile, CMake, tools
from conans import ConanFile, CMake, tools
import os

class libSqlite3Ue4Conan(ConanFile):
    name = "libsqlite3-ue4"
    version = "3.46.0"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/adamrehn/ue4-conan-recipes/libsqlite3-ue4"
    description = "libSqlite3 custom build for Unreal Engine"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"


    def source(self):
        self.run(f"git clone --branch v{self.version} --single-branch --progress --depth=1 https://github.com/creatio-ua/libsqlite3.git")
        
        # Uncomment if CMake variables need to have non-default values
        #tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        #tc.variables["SQLITE_ENABLE_COLUMN_METADATA"] = self.options.enable_column_metadata
        #tc.variables["SQLITE_ENABLE_JSON1"] = self.options.enable_json1
        #tc.variables["SQLITE_ENABLE_RTCC"] = self.options.enable_rtcc
  

    def build(self):
        tools.replace_in_file("libsqlite3/CMakeLists.txt", 
            re.compile(r"# Linking\s*target_link_libraries\(sqlite3\)", re.IGNORECASE),
                        """
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