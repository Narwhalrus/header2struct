# Directorys
SRCDIR = ../main
LIBDIR = ../../lib
ODIR = ../obj
IDIR = ../include
BINDIR = ../../bin
TESTDIR = ../test

TOPO = /usr/sim/prod/topo/v3.0
 
# Program
LIBRARY = $(LIBDIR)/libshm_iface.so
 
# Compilers
CC = gcc
 
# Source files
CSRC = $(wildcard $(SRCDIR)/*.c)
 
# Object files to be compiled with
# language dependent compilers
_COBJ = $(CSRC:.c=.o)
 
# Replace source director with object directory
COBJ = $(subst $(SRCDIR)/, $(ODIR)/, $(_COBJ))
 
# Compiler flags
LIBFLAGS = -fPIC -shared -m32
CFLAGS = -g -Wall -fPIC -m32
TFLAGS = -g -Wall -m32
 
# Libs
LIBS = -ltopo \
	   -lscramnet
 
# Include directories
INCLUDE = -I. -I$(IDIR) -I$(TOPO)/src/include
 
# Lib path
LIB = -L. -L$(LIBDIR) -L/usr/local/lib -L$(TOPO)/lib -L/usr/X11R6/lib -L/usr/local/lib/simlib
 
# Compile C object files
$(ODIR)/%.o: $(SRCDIR)/%.c
	$(CC) -c $(INCLUDE) -o $@ $< $(CFLAGS)
 
# Link both C and C++ compiled object
# files using g++ as linker
all: $(LIBRARY)
 
$(LIBRARY): $(COBJ)
	$(CC) $(LIB) $(LIBFLAGS) -o $@ $^ -ltopo -lscramnet
 
clean:
	rm -f $(ODIR)/*.o $(LIBRARY) 

cleantest:
	rm -f $(TEST)
