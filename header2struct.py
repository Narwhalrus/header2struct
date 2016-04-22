from __future__ import print_function
import sys
from pprint import pprint

sys.path.extend(['./pycparser', './pycparser/pycparser'])

from pycparser import parse_file, c_parser, c_ast

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
  ast = parse_file(filename, use_cpp=True)
  ast.show()
  sv = struct_visitor()
  sv.visit(ast)
  return sv.structs
    

if __name__ == '__main__':
  pprint(generate_struct_defs(sys.argv[1]))
