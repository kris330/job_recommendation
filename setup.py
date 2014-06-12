from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext


setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension("_jobrmd", ["_pyjobrmd.pyx"],
    	language="c++",
    	include_dirs=[
    			"jobrmd/include",
    			"libs/keywords/include",
    			"libs/segments/include",
    			"libs/eigen"
    		],
    	library_dirs=[
    			"jobrmd/lib",
    			"libs/keywords/lib",
    			"libs/segments/lib",
    		],
    	libraries=[
    			"jobrmd", "keyword", "segments"
    		]
    	)]
)
