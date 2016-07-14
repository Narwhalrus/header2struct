from ctypes import *
from mem_utils import MemSect

class shm_wrapper:
	def __init__(self, cnfg_path):
		assert isinstance(cnfg_path, str), "Config path must be a string."
	
		self.shm_iface_lib = CDLL("./libshm_iface.so")
		self.shm_iface_lib.init_memmap(c_char_p(cnfg_path))
		self._getSectNames()

	def _getSectNames(self):
		# Set return and arg types to void pointer so
		# our string array has the same base address
		# in python as in the library	
	
		# Set foreign fnc return and arg types
		get_memmap_areas = self.shm_iface_lib.get_memmap_areas
		get_memmap_areas.restype = c_void_p
		get_memmap_areas.argtypes = []
		
		free_names = self.shm_iface_lib.free_names
		free_names.argtypes = [c_void_p]
		free_names.restype = None
		
		names_c = get_memmap_areas()
		name_array = cast(names_c, POINTER(c_char_p))
	
		self.sectNames = []	
		for name in name_array:
			if not name:
				break
			self.sectNames.append(name)
		
		free_names(names_c)
		
	def attach(self, sect_name):
		if sect_name not in self.sectNames:
			print "No section %s in memmap." % (sect_name)
			return None

		# Set return and arg types
		get_memmap_area = self.shm_iface_lib.get_memmap_area
		get_memmap_area.restype = c_void_p
		get_memmap_area.argtypes = [c_char_p]

		get_memmap_area_size = self.shm_iface_lib.get_memmap_area_size
		get_memmap_area_size.restype = c_int
		get_memmap_area_size.argtypes = [c_char_p]

		sect_data_ptr = get_memmap_area(c_char_p(sect_name))
		sect_size = get_memmap_area_size(c_char_p(sect_name))

		#sect_data_buffer = cast(sect_data_ptr, POINTER(c_ubyte))
		return MemSect(sect_data_ptr, sect_size)

	def attach_struct(self, sect_name, gened_type):
		''' Generate a class attached to section of shared memory
			specified by sect_name based on C struct structName
			as found in src and return class '''
		
		if sect_name not in self.sectNames:
			print "No section %s in memmap." % (sect_name)
			return None
		
		# Set return and arg types
		get_memmap_area = self.shm_iface_lib.get_memmap_area
		get_memmap_area.restype = c_void_p
		get_memmap_area.argtypes = [c_char_p]

		get_memmap_area_size = self.shm_iface_lib.get_memmap_area_size
		get_memmap_area_size.restype = c_int
		get_memmap_area_size.argtypes = [c_char_p]

		sect_data_ptr = get_memmap_area(c_char_p(sect_name))
		sect_size = get_memmap_area_size(c_char_p(sect_name))

		if sizeof(gened_type) > sect_size:
			print "Generated structure larger than shm section."
			return None

		# Attach structure to shm sect
		boundStruct = cast(sect_data_ptr, POINTER(gened_type)).contents

		return boundStruct
			
if __name__ == "__main__":
        import header2struct
	shm = shm_wrapper("/usr/sim/intg/relentless/config")
	memSect = shm.attach("cls")
	print memSect[1].as_int32()
	
