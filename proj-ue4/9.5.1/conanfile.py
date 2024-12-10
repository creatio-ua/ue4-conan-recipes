from conans import ConanFile, CMake, tools
import os

class ProjUe4Conan(ConanFile):
    name = "proj-ue4"
    version = "9.5.1"
    license = "MIT"
    url = "https://github.com/adamrehn/ue4-conan-recipes/proj-ue4"
    description = "PROJ custom build for Unreal Engine"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"
    requires = (
        "cmake/3.24.4",
        "libcxx/ue4@adamrehn/profile",
        "ue4util/ue4@adamrehn/profile"
        )
        
    
    def cmake_flags(self):
        from ue4util import Utility
        curl= self.deps_cpp_info["libcurl"]
        sqlite = self.deps_cpp_info["libsqlite3-ue4"]
        tiff= self.deps_cpp_info["LibTiff"]
        paths = [
            curl.rootpath, 
            sqlite.rootpath,
            tiff.rootpath]
        return [
            "-DCMAKE_PREFIX_PATH={}".format(";".join(paths)),
            "-DBUILD_TESTING=OFF",
            "-DBUILD_APPS=OFF",
            "-DCMAKE_BUILD_TYPE=Release", # TODO: Review this solution
            "-DBUILD_SHARED_LIBS=OFF",
        ]
        
        
    def requirements(self):
        self.requires("libcurl/ue4@adamrehn/{}".format(self.channel))
        self.requires("libsqlite3-ue4/3.46.0@adamrehn/{}".format(self.channel))
        self.requires("LibTiff/ue4@adamrehn/{}".format(self.channel))


    def source(self):
        # Clone the source code
        self.run("git clone --progress --depth=1 https://github.com/OSGeo/PROJ.git -b {}".format(self.version))
    

    def build(self):
        # Enable compiler interposition under Linux to enforce the correct flags for libc++
        from libcxx import LibCxx
        LibCxx.set_vars(self)

        cmake = CMake(self)
        cmake.configure(source_folder="proj", args=self.cmake_flags())
        cmake.build()
        cmake.install()
    
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
