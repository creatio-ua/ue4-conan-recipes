from conans import ConanFile, CMake, tools

class MergetiffUe4Conan(ConanFile):
    name = "mergetiff-ue4"
    version = "0.0.19"
    license = "MIT"
    url = "https://github.com/adamrehn/ue4-conan-recipes/mergetiff-ue4"
    description = "mergetiff header-only package for Unreal Engine 4"
    generators = "cmake", "cmake_find_package"
    requires = (
        "cmake/3.24.2"
        )
    
    def source(self):
        self.run("git clone --progress --depth=1 https://github.com/adamrehn/mergetiff-cxx.git -b v{}".format(self.version))
    
    def requirements(self):
        self._requireUnreal("gdal-ue4/3.10.0@adamrehn/{}".format(self.channel))
    
    def build(self):
        
        # Install the mergetiff headers
        cmake = CMake(self)
        cmake.configure(source_folder="mergetiff-cxx", args=[
            "-DHEADER_ONLY=ON",
            "-DGDAL_DIR={}".format(self.deps_cpp_info["gdal-ue4"].rootpath)])
        cmake.install()
