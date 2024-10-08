cmake_minimum_required(VERSION 3.17.2...3.29)
project(${SKBUILD_PROJECT_NAME})
find_package(
  Python
  COMPONENTS Interpreter Development.Module NumPy
  REQUIRED)

set(f2py_module_name "regionalised_dailyT")
set(fortran_src_file "${CMAKE_CURRENT_SOURCE_DIR}/regionalised_dailyT.for")
# message(FATAL_ERROR )


add_custom_target(${f2py_module_name} ALL)

add_custom_command(
  TARGET ${f2py_module_name}
  # OUTPUT ${generated_module_file}
  COMMAND ${PYTHON_EXECUTABLE}
    -m "numpy.f2py"
    -c ${fortran_src_file}
    -m ${f2py_module_name}
    -I ${CMAKE_CURRENT_SOURCE_DIR}
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  )

if (WIN32)
  # set(generated_module_file ${CMAKE_CURRENT_BINARY_DIR}/libregional.HM4X2VRITDPUZ22SXJ2CC7VFRHQR5TXG.gfortran-win_amd64.dll)
  FILE(GLOB generated_module_file *.pyd)
  FILE(GLOB generated_dll regionalised_dailyT/.libs/*.dll)
  install(FILES ${generated_dll} DESTINATION pyraingen/fortran_daily/regionalised_dailyT/.libs)
elseif(APPLE)
  message(ERROR "osx is unsupported")
else()
  # set(generated_module_file ${CMAKE_CURRENT_BINARY_DIR}/${f2py_module_name}.cpython-${Python_VERSION_MAJOR}${Python_VERSION_MINOR}-x86_64-linux-gnu.so)
  FILE(GLOB generated_module_file *.so)
endif (WIN32)

# add_custom_target(${f2py_module_name} ALL
#   DEPENDS ${generated_module_file}
#   )

install(FILES ${generated_module_file} DESTINATION pyraingen/fortran_daily)