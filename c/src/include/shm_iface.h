#ifndef _SHM_IFACE_H_
#define _SHM_IFACE_H_
#ifdef __cplusplus
extern "C" {
#endif

void handle_error(const char *error_str);

void init_memmap(const char *memmap_path);
char **get_memmap_areas(void);
void free_names(char **names);
int get_memmap_area_size(const char *memmap_area);
void *get_memmap_area(char *memmap_area);

#ifdef __cplusplus
}
#endif
#endif /* _SHM_IFACE_H_ */
