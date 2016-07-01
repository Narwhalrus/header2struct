#!/usr/bin/python

from __future__ import print_function
import sys
import ctypes
import json
import struct
from collections import OrderedDict
from pprint import pprint
import operator


try:
  from pycparser import parse_file, c_parser, c_ast
except ImportError:
  sys.path.extend(['./pycparser', './pycparser/pycparser', './pycparserext', './pycparserext/pycparserext'])
  from pycparser import parse_file, c_parser, c_ast

op_map = {
  "*": operator.mul,
  "+": operator.add,
  "-": operator.sub,
  "/": operator.div
}

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


def resolve_binary_op(binary_op_obj):

  op_fnc = op_map.get(binary_op_obj.op)
  if op_fnc == None:
    print('Could not find operator function for', binary_op_obj.op)
    return 0

  left = binary_op_obj.left
  right = binary_op_obj.right

  if isinstance(left, c_ast.BinaryOp):
    left_val = resolve_binary_op(left)
  else:
    left_val = int(left.value)
    
  if isinstance(right, c_ast.BinaryOp):
    right_val = resolve_binary_op(right)
  else:
    right_val = int(right.value)

  return op_fnc(left_val, right_val)
  
# This class takes a single Struct AST node and parses out all the fields
class struct_def_generator(c_ast.NodeVisitor):
  def __init__(self, struct_id):
    self.struct_id = struct_id
    self.fields = []

  def generate(self, struct_node):
    self.visit(struct_node)
    return self.fields

  # TODO: This method probably isn't very robust right now. 
  def visit_Decl(self, node):
    name = node.name
    # For unnamed structs and unions 
    if name == None:
      #name = self.struct_id
      # If our decl is unnamed, just name it after the type
      name = node.type.name

    print('PROCESSING', name)

    dims = []
    # TODO: Assumption: type will either be a TypeDecl (basic types and structs),
    # or an ArrayDecl.
    field_type = node.type
    is_array = False

    # If type is an array decl then we have to loop through each
    # dimension of the array decl to get to TypeDecl (basic type or struct)
    # We'll also accumulate array dimensions
    while isinstance(field_type, c_ast.ArrayDecl):
      is_array = True
      print('******************')
      print(type(node.type.dim).__name__)
      array_size = 0
      # We have to resolve an expression in our array def
      if isinstance(node.type.dim, c_ast.BinaryOp):
        op = node.type.dim
        print('Found binary op')
        print(type(op.op), op)
        # TODO: Remember to remove
        array_size = resolve_binary_op(op)
        print('Resolved binary op to', array_size)
      else:
        array_size = int(node.type.dim.value)
        
      dims.append(array_size)
      field_type = field_type.type
    
    if not is_array:
      dims.append(1)

    # Now that we have to base TypeDecl, "dereference" it to figure
    # out if it's an IndentifierType (basic type) or Struct (struct)
    # TODO: Assumption: These are the only two values of a TypeDecl.
    # Try testing with a typedef of a basic type and see what happens.
    # I'll probably have to keep track of all typedefs and resolve at some
    # point...
    if isinstance(field_type, c_ast.TypeDecl):
      field_type = field_type.type
    else:
      print('I guess this doesnt have a type decl...')

    # Handle structs and basic types differently
    if isinstance(field_type, c_ast.Struct) or isinstance(field_type, c_ast.Union):
      # If structure name is None, we're dealing with an anonymous struct
      if field_type.name == None:
        typename = '<anonymous_struct>' 
      else:
        typename = field_type.name
    else:
      typename = field_type.names
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
    self.unions = {}
    self._unnamed_unions = 1
    self._unnamed_structs = 1

  def visit_Struct(self, node):
    if len(node.children()) > 0:
      if node.name == None:
        name = self.current_parent.declname
        # Looks like an anonymous struct or a typedef'd struct. Just make the name the
        # typename or varname
        if isinstance(self.current_parent, c_ast.TypeDecl):
          name = self.current_parent.declname
        else:
          #name = 'unnamed_struct_%d' % (self._unnamed_structs)
          node.name = 'unnamed_struct_%d' % (self._unnamed_structs)
          name = node.name
          #name = 'unnamed'
          self._unnamed_structs += 1
      else:
        name = node.name

      #s_gen = struct_def_generator(name)
      #self.structs[name] = s_gen.generate(node)
      self.structs[name] = node

    old_parent = self.current_parent
    self.current_parent = node
    for c_name, c in node.children():
      self.visit(c)
    self.current_parent = old_parent

  # Only difference between struct and union visitor is the dict it stores definitions in
  def visit_Union(self, node):
    if len(node.children()) > 0:
      if node.name == None:
        # Looks like an anonymous struct or a typedef'd struct. Just make the name the
        # typename or varname
        if isinstance(self.current_parent, c_ast.TypeDecl):
          name = self.current_parent.declname
        else:
          #name = 'unnamed_union_%d' % (self._unnamed_unions)
          node.name = 'unnamed_union_%d' % (self._unnamed_unions)
          name = node.name
          self._unnamed_unions += 1
      else:
        name = node.name

      #s_gen = struct_def_generator(name)
      #self.unions[name] = s_gen.generate(node)
      self.unions[name] = node

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


class typedef_resolver(c_ast.NodeVisitor):
  def __init__(self):
    self.typedef_map = {}

  def visit_Typedef(self, node):
    print('**************************')
    print ('IN TYPEDEF VISIT!')
    print('**************************')
    name = node.name
    type_decl = node.type
    print(type_decl.declname)
    alias = type_decl.declname
    if isinstance(type_decl.type, c_ast.IdentifierType):
      typename = ' '.join(type_decl.type.names)
      self.typedef_map[alias] = typename
      print(alias,':',typename)

    

def generate_struct_defs(filename):
  ast = parse_file(filename, use_cpp=True)
  ast.show()
  sv = struct_visitor()
  sv.visit(ast)
  
  tdr = typedef_resolver()
  tdr.visit(ast)

  
  parsed_structs = dict([(name, struct_def_generator(name).generate(node)) for name, node in sv.structs.iteritems()])
  parsed_unions = dict([(name, struct_def_generator(name).generate(node)) for name, node in sv.unions.iteritems()])

  return parsed_structs, parsed_unions

# TODO: Add alignment kwarg
# TODO: With addition of Union type, names make less sense. Fix
def generate_ctypes_struct(struct_defs, union_defs, struct_name):
  struct_fields = []

  # TODO: 'struct' and 'union' should probably be enums instead
  udt_type = 'struct'
  struct_def = struct_defs.get(struct_name)
  if struct_def == None:
    udt_type = 'union'
    struct_def = union_defs.get(struct_name)
    if struct_def == None:
      print("Could not find type %s in structure/union dictionaries. Exiting..." % (struct_name))
      exit(1)

  for field in struct_def:
    varname, typename, dims = field
    
    field_type = c_type_map.get(typename)
    # Right now type is either a basic type or a struct in our struct_defs
    if field_type == None:
      if typename == '<anonymous_struct>':
        typename = varname
      field_type = generate_ctypes_struct(struct_defs, union_defs, typename)

    # Handle array types
    for dim in dims:
      if dim > 1:
        field_type *= dim

    struct_fields.append((varname, field_type))


  if udt_type == 'struct':
    base_cls = ctypes.Structure
  else:
    base_cls = ctypes.Union
    
  class temp_struct(base_cls):
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

# kwargs are options passed to json.dumps
def struct2json(ct_struct, **kwargs):
  return json.dumps(getdict(s), kwargs)

def read_simple_bin_file(filename, struct_type):
  with open(filename, 'rb') as ifile:
    struct_size = struct.unpack('I', ifile.read(4))[0]
    print(struct_size)

    s = struct_type() 
    for frame in iter(lambda: ifile.read(struct_size), ''):
      s.load(frame)
      print(json.dumps(getdict(s), indent=4, separators=(',',': ')))
      
if __name__ == '__main__':
  struct_defs, union_defs = generate_struct_defs(sys.argv[1])
  print('Struct defs:')
  pprint(struct_defs)
  print()

  print('Union defs:')
  pprint(union_defs)
  print()

  print('Generating ctypes Structure...')
  if len(sys.argv) > 2:
    struct_name = sys.argv[2]
  else:
    struct_name = 'nd_struct'

  gened_struct = generate_ctypes_struct(struct_defs, union_defs, struct_name)
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

  #read_simple_bin_file('outbin.bin', gened_struct)


