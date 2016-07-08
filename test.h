typedef int integer;

struct n_struct
{
  integer a;
  float b[2*(3+1)];
  double c;
};

typedef struct
{
  int d;
  float e[10];
} td_struct;

typedef struct td_struct_2_s
{
  float h;
  int j;
} td_struct_2;

typedef struct
{
  struct n_struct my_n_struct;
  td_struct my_td_struct;

  union
  {
    int ua;
    char ub[4];
  } anon_union;

  union {
    int ying;
    int yang;
  };

  struct
  {
    int f;
    unsigned short g;
  } inside_decl[3];

  td_struct_2 my_td_struct_2;

} nd_struct;
