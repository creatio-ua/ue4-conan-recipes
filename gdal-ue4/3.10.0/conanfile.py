from conans import AutoToolsBuildEnvironment, ConanFile, tools, CMake

import os

class GdalUe4Conan(ConanFile):
    name = "gdal-ue4"
    version = "3.10.0"
    license = "MIT"
    url = "https://github.com/adamrehn/ue4-conan-recipes/gdal-ue4"
    description = "GDAL custom build for Unreal Engine 4"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"
    short_paths = True
    requires = (
        "cmake/3.24.2",
        "libcxx/ue4@adamrehn/profile",
        "ue4util/ue4@adamrehn/profile"
    )
    
    def _replace_multiple(self, filename, pairs):
        for pair in pairs:
            search, replace = pair
            tools.replace_in_file(filename, search, replace)
    
    def requirements(self):
        self.requires("libsqlite3-ue4/3.46.0@adamrehn/{}".format(self.channel))
        self.requires("LibTiff/ue4@adamrehn/{}".format(self.channel))
        self.requires("geos-ue4/3.6.3@adamrehn/{}".format(self.channel))
        self.requires("proj-ue4/9.5.1@adamrehn/{}".format(self.channel))
        self.requires("libcurl/ue4@adamrehn/{}".format(self.channel))
        self.requires("UElibPNG/ue4@adamrehn/{}".format(self.channel))
        self.requires("zlib/ue4@adamrehn/{}".format(self.channel))
        self.requires("OpenSSL/ue4@adamrehn/{}".format(self.channel))
        self.requires("nghttp2/ue4@adamrehn/{}".format(self.channel))
        self.requires("LibJpegTurbo/ue4@adamrehn/{}".format(self.channel))
    
    def configure_flags(self):
        
        # Determine the absolute path to `geos-config`
        from ue4util import Utility
        geos = self.deps_cpp_info["geos-ue4"]
        geosConfig = Utility.resolve_file(geos.bin_paths[0], "geos-config")
        
        return [
            "--prefix=" + self.package_folder,
            "--datarootdir={}/data".format(self.package_folder),
            "--enable-static",
            "--disable-shared",
            "--without-libtool",
            "--enable-pdf-plugin=no",
            "--without-ld-shared",
            "--with-threads=yes",
            "--with-libz={}".format(self.deps_cpp_info["zlib"].rootpath),
            "--without-liblzma",
            "--without-libiconv-prefix",
            "--without-pg",
            "--without-grass",
            "--without-libgrass",
            "--without-cfitsio",
            "--without-pcraster",
            "--with-png={}".format(self.deps_cpp_info["UElibPNG"].rootpath),
            "--without-mrf",
            "--without-dds",
            "--without-gta",
            "--with-libtiff=internal",
            "--with-geotiff=internal",
            "--with-jpeg=internal",
            "--with-rename_internal_libtiff_symbols",
            "--with-rename_internal_libgeotiff_symbols",
            "--without-jpeg12",
            "--without-gif",
            "--without-ogdi",
            "--without-fme",
            "--without-sosi",
            "--without-mongocxx",
            "--without-hdf4",
            "--without-hdf5",
            "--without-kea",
            "--without-netcdf",
            "--without-jasper",
            "--without-openjpeg",
            "--without-fgdb",
            "--without-ecw",
            "--without-kakadu",
            "--without-mrsid",
            "--without-jp2mrsid",
            "--without-mrsid_lidar",
            "--without-msg",
            "--without-bsb",
            "--without-oci",
            "--without-oci-include",
            "--without-oci-lib",
            "--without-grib",
            "--without-mysql",
            "--without-ingres",
            "--without-xerces",
            "--without-expat",
            "--without-libkml",
            "--without-odbc",
            "--with-dods-root=no",
            "--without-curl",
            "--without-xml2",
            "--without-spatialite",
            "--with-sqlite3={}".format(self.deps_cpp_info["libsqlite3-ue4"].rootpath),
            "--without-pcre",
            "--without-idb",
            "--without-sde",
            "--without-epsilon",
            "--without-webp",
            "--without-qhull",
            "--with-freexl=no",
            "--with-libjson-c=internal",
            "--without-pam",
            "--without-poppler",
            "--without-podofo",
            "--without-pdfium",
            "--without-perl",
            "--without-python",
            "--without-java",
            "--without-mdb",
            "--without-rasdaman",
            "--without-armadillo",
            "--without-cryptopp",
            "--with-zstd=no",
            "--with-proj={}".format(self.deps_cpp_info["proj-ue4"].rootpath),
            "--with-geos={}".format(geosConfig)
        ]
    
    def cmake_flags(self):
        from ue4util import Utility
        curl= self.deps_cpp_info["libcurl"]
        sqlite = self.deps_cpp_info["libsqlite3-ue4"]
        proj= self.deps_cpp_info["proj-ue4"]
        tiff= self.deps_cpp_info["LibTiff"]
        png= self.deps_cpp_info["UElibPNG"]
        zlib= self.deps_cpp_info["zlib"]

        os.environ["PROJ_DIR"] = proj.deps_cpp_info.rootpath

        self.options["zlib"].shared = False  # Use static zlib
        paths = [
            curl.rootpath, 
            sqlite.rootpath,
            proj.rootpath, 
            tiff.rootpath, 
            png.rootpath, 
            zlib.rootpath]

        return [
            "-DCMAKE_PREFIX_PATH={}".format(";".join(paths)),
            "-DCURL_LIBRARY={}".format(Utility.resolve_file(curl.lib_paths[0], curl.libs[0])),
            "-DCURL_INCLUDE_DIR={}".format(curl.include_paths[0]),
            "-DGDAL_USE_CURL=ON",
            "-DCURL_USE_STATIC_LIBS=ON",
            "-DGDAL_USE_ZLIB=ON",
            "-DGDAL_BUILD_APPS=OFF",    # Explicitly disable standalone apps
            "-DBUILD_APPS=OFF",         #
            "-DBUILD_SHARED_LIBS=OFF",
            "-DBUILD_TESTING=OFF",
        ]


    def source(self):
        self.run("git clone --progress --depth=1 https://github.com/OSGeo/gdal.git -b v{}".format(self.version))
    

    def build(self):
        # Legacy: Build GDAL using CMake under Windows and autotools under other platforms
        # The Unix build isn't tested
        with tools.chdir("./gdal/"):
            if self.settings.os == "Windows":
                self.build_windows()
            else:
                self.build_unix()
    
    def build_windows(self):
        cmake = CMake(self)
        cmake.configure(source_folder="gdal", args=self.cmake_flags())
        cmake.build()
        
    
    # This is untested
    def build_unix(self):
        
        # Enable compiler interposition under Linux to enforce the correct flags for libc++
        from libcxx import LibCxx
        LibCxx.set_vars(self)
        
        # Run autogen.sh
        self.run("./autogen.sh")

        # Patch out iconv support under Mac OS X and patch GDAL v2.4.0 for XCode 12.x
        if self.settings.os == "Macos":
            self.run("sed -i '' 's/-D_XOPEN_SOURCE=500 //g' ogr/ogrsf_frmts/geojson/libjson/GNUmakefile")
            tools.replace_in_file("./configure", "iconv.h", "iconv_h")
        
        # Patch out iconv support under Linux, since the UE4 bundled toolchain doesn't include it
        if self.settings.os == "Linux":
            tools.replace_in_file("./configure", "iconv.h", "iconv_h")
        
        # Under Linux, the UE4-bundled version of zlib is typically named libz_fPIC.a, but GDAL expects libz.a
        zlibName = self.deps_cpp_info["zlib"].libs[0]
        if zlibName != "z":
            tools.replace_in_file("./configure", "-lz", "-l{}".format(zlibName))
        
        # Prepare the autotools build environment
        autotools = AutoToolsBuildEnvironment(self)
        LibCxx.fix_autotools(autotools)
        
        # Ensure the configure script can load the GEOS shared library when running tests
        geosPaths = self.deps_cpp_info["geos-ue4"].lib_paths
        ldPath = ":".join([os.environ.get("LD_LIBRARY_PATH", "")] + geosPaths)
        
        # Build using autotools
        with tools.environment_append({"LD_LIBRARY_PATH": ldPath}):
            autotools.configure(args=self.configure_flags())
            autotools.make(args=["-j{}".format(tools.cpu_count())])
            autotools.make(target="install")
    
    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.resdirs = ["data"]
        if self.settings.os == "Windows":
            sdk_dir = os.environ.get("WindowsSdkDir")
            if sdk_dir:
                wbemuuid_path = os.path.join(sdk_dir, "Lib", "um", "x64", "wbemuuid.lib")
                self.cpp_info.exelinkflags.append(wbemuuid_path)
            else:
                self.cpp_info.system_libs.append("wbemuuid.lib")  # Fallback
