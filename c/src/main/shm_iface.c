#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <sys/shm.h>

#include "sma_int.h"
#include "sma.h"
#include "shm_iface.h"
extern sma_data_t _sma;

static char path[1024];
short int new_sect_byte;
size_t size;
char *memmap_storage;
sma_sect_t *sect;
const int DATA_ARRAY_SIZE = 50;
static char memname[50][20];
static int memsize[50];
static int num_mmareas;
static void *mmarea;

void handle_error(const char *error_str)
{
	if(errno) {
		perror(error_str);
	} else {
		printf("ERROR: %s\n", error_str);
	}
}

void init_memmap(const char *memmap_path) 
{
	int i;
	char *path_str;

	if(setenv("CNFG", memmap_path, 0) < 0) {
		handle_error("Could not set CNFG environment variable.");
		return;
	}
	
	path_str = getenv("CNFG");
	if(!path_str) {
		handle_error("Could not get CNFG environment variable.");
		return;
	}

	strncpy(path, path_str, 1024);

	// Init shm sections
	sma_init();

	printf("MEMMAP section info\n");
	
	i = 0;
	for(sect = _sma.sect; sect; sect = sect->next) {
		// Get pointer to current shm section
		memmap_storage = sma_shm_get(sect->name, sect->msize);

		// Save section name and size
		sprintf(memname[i], sect->name);
		memsize[i] = sect->msize;
	
		// Make it pretty	
		printf("'%s'\n", memname[i]);
		printf("\tidx: %d\n", i);
		printf("\taddr: %p\n", memmap_storage);
		printf("\tsize: %d\n", memsize[i]);
		printf("\n");

		i++;
	}	

	num_mmareas = i + 1;
}

char **get_memmap_areas()
{
	int i;
	char **ret;
	
	ret = malloc(num_mmareas * sizeof(char *));
	for(i = 0; i < num_mmareas; i++) {
		ret[i] = calloc(20, 20 * sizeof(char));
		strncpy(ret[i], memname[i], 20);
	}
	
	return ret;
}

void free_names(char **names)
{
	int i;
	for(i = 0; i < num_mmareas; i++) {
		free(names[i]);
	}
	free(names);
}

// Probably unnecessary...
int get_memmap_area_size(const char *memmap_area)
{
	int i;
	for(i = 0; i < DATA_ARRAY_SIZE; i++) {
		if(strcmp(memmap_area, memname[i]) == 0) {
			return memsize[i];
		}
	}

	return -1;
}

void *get_memmap_area(char *memmap_area)
{
	if(!(mmarea = sma_shm_get(memmap_area, 0))) {
		fprintf(stderr, "Couldn't attach to '%s'\n", memmap_area);
		return NULL;
	} else {
		printf("Successfully attached to '%s' (%p)\n", memmap_area, mmarea);
	}

	return mmarea;
}
	

