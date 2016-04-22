struct n_struct
{
  int a;
  float b;
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

  struct
  {
    int f;
    unsigned short g;
  } inside_decl[3];

} nd_struct;
