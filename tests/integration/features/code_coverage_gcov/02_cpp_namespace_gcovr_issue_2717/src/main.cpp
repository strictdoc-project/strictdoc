#include <iostream>

#include "functions.h"

int main() {
  test::Adder adder;
  test::Multiplier multiplier;

  std::cout << adder.add(2, 3) << "\n";
  std::cout << multiplier.multiply(4, 5) << "\n";

  return 0;
}
