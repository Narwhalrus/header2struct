typedef int integer;

struct n_struct
{
  integer a;
  float b[1*(3+1)];
  double c;
};

typedef struct
{
  int d;
  float e[10];
} td_struct;

typedef struct
{
  struct n_struct my_n_struct;
  td_struct my_td_string;

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

} nd_struct;
