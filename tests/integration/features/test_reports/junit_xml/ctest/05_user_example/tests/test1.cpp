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

TEST(MyTestSuiteName, TestName)
{
    // Test it
    EXPECT_EQ(Multiplication(2, 2), 4);
}

class MyTestHelper : public testing::Test
{
   protected:
   MyTestHelper()
    {
        // Setup MyTestHelper
    }
};

TEST_F(MyTestHelper, TestName2)
{
    // Test it
    EXPECT_EQ(Multiplication(1, 4), 4);
}

class MyTestHelperPattern : public testing::TestWithParam<int>
{
};

INSTANTIATE_TEST_SUITE_P(MyTestPattern, MyTestHelperPattern, testing::Values(1, 2, 3));

TEST_P(MyTestHelperPattern, TestName3)
{
    // Test it
    EXPECT_NE(Multiplication(GetParam(), GetParam()), 0);
}
