#!/bin/bash

# Unload CEN-IT python modules because they break the PYTHONPATH
module unload python3 python

# Define base path to radiative transfer course
RTPATH="/data/share/lehre/unix/rtcourse"

# Set environment variables where to find ...
# ... the ARTS API
export ARTS_BUILD_PATH="$RTPATH/arts/build"

# ... and ARTS auxiliary data,
export ARTS_DATA_PATH="$RTPATH/arts-xml-data:$ARTS_DATA_PATH"
export ARTS_DATA_PATH="$RTPATH/catalogue:$ARTS_DATA_PATH"
export ARTS_INCLUDE_PATH="$RTPATH/arts/controlfiles:$ARTS_INCLUDE_PATH"

# Setup the user search path to include the ARTS binary
# and our Anaconda Python Distribution.
export PATH="$RTPATH/arts/build/src:$RTPATH/anaconda3/bin:$PATH:$RTPATH/bin"
