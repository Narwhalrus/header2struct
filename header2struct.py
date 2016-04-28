#!/usr/bin/python

from __future__ import print_function
import sys
import ctypes
import json
import struct
from collections import OrderedDict
from pprint import pprint

sys.path.extend(['./pycparser', './pycparser/pycparser', './pycparserext', './pycparserext/pycparserext'])

from pycparser import parse_file, c_parser, c_ast
#from pycparserext.ext_c_parser import GnuCParser

# This class takes a single Struct AST node and parses out all the fields
class struct_def_generator(c_ast.NodeVisitor):
  def __init__(self, struct_id):
    print('Generating struct for', struct_id)
    self.struct_id = struct_id
    self.fields = []

  def generate(self, struct_node):
    self.visit(struct_node)
    return self.fields

  # TODO: This method probably isn't very robust right now. 
  def visit_Decl(self, node):
    name = node.name
    dims = []
    # TODO: Assumption: type will either be a TypeDecl (basic types and structs),
    # or an ArrayDecl.
    type = node.type
    is_array = False

    # If type is an array decl then we have to loop through each
    # dimension of the array decl to get to TypeDecl (basic type or struct)
    # We'll also accumulate array dimensions
    while isinstance(type, c_ast.ArrayDecl):
      is_array = True
      dims.append(int(node.type.dim.value))
      type = type.type
    
    if not is_array:
      dims.append(1)

    # Now that we have to base TypeDecl, "dereference" it to figure
    # out if it's an IndentifierType (basic type) or Struct (struct)
    # TODO: Assumption: These are the only two values of a TypeDecl.
    # Try testing with a typedef of a basic type and see what happens.
    # I'll probably have to keep track of all typedefs and resolve at some
    # point...
    type = type.type

    # Handle structs and basic types differently
    if isinstance(type, c_ast.Struct):
      # If structure name is None, we're dealing with an anonymous struct
      if type.name == None:
        typename = '<anonymous_struct>' 
      else:
        typename = type.name
    else:
      typename = type.names
      # a type 'unsigned x' would be stored as ['unsigned', 'x']
      # just flatten and parse out when generating ctypes struct
      typename = ' '.join(typename)

    # TODO: Replace with named tuple
    field = (name, typename, dims)
    self.fields.append(field)

# This visitor finds all structures in the file being parsed.
class struct_visitor(c_ast.NodeVisitor):
  def __init__(self):
    self.current_parent = None
    self.structs = {}

  def visit_Struct(self, node):
    if len(node.children()) > 0:
      if node.name == None:
        name = self.current_parent.declname
      else:
        name = node.name

      s_gen = struct_def_generator(name)
      self.structs[name] = s_gen.generate(node)

    old_parent = self.current_parent
    self.current_parent = node
    for c_name, c in node.children():
      self.visit(c)
    self.current_parent = old_parent


  def generic_visit(self, node):
    old_parent = self.current_parent
    self.current_parent = node
    for c_name, c in node.children():
      self.visit(c)
    self.current_parent = old_parent

def generate_struct_defs(filename):
  #p = GnuCParser()
  ast = parse_file(filename, use_cpp=True)
  #ast = p.parse(open(filename, 'rb').read())
  ast.show()
  sv = struct_visitor()
  sv.visit(ast)
  return sv.structs

c_type_map = {
    'int': ctypes.c_int,
    'unsigned int': ctypes.c_uint,
    'unsigned': ctypes.c_uint,
    'char': ctypes.c_byte,
    'unsigned char': ctypes.c_ubyte,
    'float': ctypes.c_float,
    'double': ctypes.c_double,
    'short': ctypes.c_short,
    'unsigned short': ctypes.c_ushort
}

def generate_ctypes_struct(struct_defs, struct_name):
  struct_def = struct_defs[struct_name]
  struct_fields = []

  for field in struct_def:
    varname, typename, dims = field
    field_type = c_type_map.get(typename)
    # Right now type is either a basic type or a struct in our struct_defs
    if field_type == None:
      if typename == '<anonymous_struct>':
        typename = varname
      field_type = generate_ctypes_struct(struct_defs, typename)

    # Handle array types
    for dim in dims:
      if dim > 1:
        field_type *= dim

    struct_fields.append((varname, field_type))
    
  class temp_struct(ctypes.Structure):
    _fields_ = struct_fields

    # Add this load method to make loading from a
    # python byte string easier
    def load(self, bytes):
      fit = min(len(bytes), ctypes.sizeof(self))
      ctypes.memmove(ctypes.addressof(self), bytes, fit)

  temp_struct.__name__ = struct_name

  return temp_struct

#TODO: This can be made better.
def getdict(ct_struct):
  result = OrderedDict()
  for field, _ in ct_struct._fields_:
    value = getattr(ct_struct, field)
    if (type(value) not in [int, long, float, bool]) and not bool(value):
      value = None
    elif hasattr(value, "_length_") and hasattr(value, "_type_"):
      value = list(value)
      if hasattr(value[0], "_fields_"):
        value = [getdict(s) for s in value]
    elif hasattr(value, "_fields_"):
      value = getdict(value)
    result[field] = value

  return result


def read_simple_bin_file(filename, struct_type):
  with open(filename, 'rb') as ifile:
    struct_size = struct.unpack('I', ifile.read(4))[0]
    print(struct_size)

    s = struct_type() 
    for frame in iter(lambda: ifile.read(struct_size), ''):
      s.load(frame)
      print(json.dumps(getdict(s), indent=4, separators=(',',': ')))
      


if __name__ == '__main__':
  struct_defs = generate_struct_defs(sys.argv[1])
  print('Struct defs:')
  pprint(struct_defs)
  print()

  print('Generating ctypes Structure...')
  gened_struct = generate_ctypes_struct(struct_defs, 'nd_struct')
  print('Gened struct:')
  print('\ttype:', type(gened_struct))
  print('\tsizeof:', ctypes.sizeof(gened_struct))
  print('\tfields:')
  for field in gened_struct._fields_:
    print('\t\t', field)
  print()

  gs = gened_struct()
  json_out = json.dumps(getdict(gs), indent=4, separators=(',',': '))
  print(json_out)

  read_simple_bin_file('outbin.bin', gened_struct)


