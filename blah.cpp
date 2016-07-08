#include <string>
#include <iostream>
#include <fstream>

#include "test.h"

using namespace std;

int main()
{
  nd_struct test_struct = {};

  ofstream outbin("outbin.bin", ios::out | ios::binary);
  
  unsigned struct_size = sizeof(nd_struct);
  outbin.write(reinterpret_cast<char *>(&struct_size), sizeof(unsigned));

  for(int i = 0; i < 100; i++) {
    outbin.write(reinterpret_cast<char *>(&test_struct), sizeof(nd_struct));
    test_struct.inside_decl[1].f++;
    test_struct.my_n_struct.a++;
    test_struct.my_td_struct_2.h += 0.1;
    test_struct.my_n_struct.c += 0.2;
    test_struct.anon_union.ua = 255;
  }

  outbin.close();
}

