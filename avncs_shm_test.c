#include <stdio.h>
#include <stdlib.h>

#include "shm_iface.h"
#include "mmd_to_avncs.h"



int main()
{
  init_memmap(getenv("CNFG"));

  mmd_to_avncs_type *mmd2avncs = NULL;

  mmd2avncs = (mmd_to_avncs_type *)get_memmap_area("AVNCS");

  printf("%f\n", mmd2avncs->gps.latitude);
}
