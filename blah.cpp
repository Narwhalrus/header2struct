#include <string>
#include <iostream>

using namespace std;

int main()
{
  string str;
  while(getline(std::cin, str, ' ')) {
    cout << str << endl;
  }

  return 0;
}

