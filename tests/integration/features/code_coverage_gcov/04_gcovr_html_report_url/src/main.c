#include <stdio.h>

void function_covered(void) {
  printf("This function is covered\n");
}

void function_not_covered(void) {
  printf("This function is not covered\n");
}

int main(void) {
  function_covered();
}
