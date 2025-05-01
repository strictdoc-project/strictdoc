#include <gtest/gtest.h>

//
// Code that we want to test
//

int Multiplication(int value1, int value2)
{
    // Multiply like a boss
    return value1 * value2;
}

//
// GTest code below
//

TEST(TestCaseVc, TestCase)
{
    // Test it
    EXPECT_EQ(Multiplication(2, 2), 4);
}

TEST(TestCaseVc, Steering1)
{
    // Test it
    EXPECT_EQ(Multiplication(2, 2), 4);
}
