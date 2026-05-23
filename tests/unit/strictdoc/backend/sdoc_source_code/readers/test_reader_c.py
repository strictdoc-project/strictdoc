"""
@relation(SDOC-SRS-146, scope=file)
"""

from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.reader_c import (
    SourceFileTraceabilityReader_C,
)


def test_00_empty_file():
    input_string = b""""""

    reader = SourceFileTraceabilityReader_C()

    info = reader.read(input_string, file_path="NOT_RELEVANT")

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 0


def test_01_single_string():
    input_string = b"""\
// Unimportant comment.
"""

    reader = SourceFileTraceabilityReader_C()

    info = reader.read(input_string, file_path="NOT_RELEVANT")

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.functions) == 0
    assert len(info.markers) == 0


def test_02_functions():
    input_string = b"""\
#include <stdio.h>

/**
 * Some text.
 *
 * @relation(REQ-1, scope=function)
 */
void hello_world(void) {
    print("hello world\\n");
}

/**
 * Some text.
 *
 * @relation(REQ-2, scope=function)
 */
void hello_world_2(void) {
    print("hello world\\n");
}
"""

    reader = SourceFileTraceabilityReader_C()

    info: SourceFileTraceabilityInfo = reader.read(
        input_string, file_path="foo.c"
    )

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 2
    assert info.markers[0].ng_source_line_begin == 6
    assert info.markers[0].ng_range_line_begin == 3
    assert info.markers[0].ng_range_line_end == 10
    assert info.markers[0].reqs_objs[0].ng_source_line == 6
    assert info.markers[0].reqs_objs[0].ng_source_column == 14

    assert info.markers[1].ng_source_line_begin == 15
    assert info.markers[1].ng_range_line_begin == 12
    assert info.markers[1].ng_range_line_end == 19
    assert info.markers[1].reqs_objs[0].ng_source_line == 15
    assert info.markers[1].reqs_objs[0].ng_source_column == 14


def test_03_functions_multiline():
    input_string = b"""\
#include <stdio.h>

/**
 * Some text.
 *
 * @relation(
 *   REQ-1, scope=function
 * )
 */
void hello_world(void) {
    print("hello world\\n");
}

/**
 * Some text.
 *
 * @relation(REQ-2,
 * scope=function)
 */
void hello_world_2(void) {
    print("hello world\\n");
}
"""

    reader = SourceFileTraceabilityReader_C()

    info: SourceFileTraceabilityInfo = reader.read(
        input_string, file_path="foo.c"
    )

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 2
    assert info.markers[0].ng_source_line_begin == 6
    assert info.markers[0].ng_range_line_begin == 3
    assert info.markers[0].ng_range_line_end == 12
    assert info.markers[0].reqs_objs[0].ng_source_line == 7
    assert info.markers[0].reqs_objs[0].ng_source_column == 6

    assert info.markers[1].ng_source_line_begin == 17
    assert info.markers[1].ng_range_line_begin == 14
    assert info.markers[1].ng_range_line_end == 22
    assert info.markers[1].reqs_objs[0].ng_source_line == 17
    assert info.markers[1].reqs_objs[0].ng_source_column == 14


def test_04_multiline_markers_with_underscores():
    """
    Bug: requirements UID not detected in source code when there's an EOL #2130
    https://github.com/strictdoc-project/strictdoc/issues/2130
    """

    input_string = b"""\
#include <stdio.h>

/**
 * @brief some text
 * @return some text.
 * @param[in] void
 * @param[out] void
 * @param[in, out] void
 * @pre
 * @post
 * @relation{INT_STP_016_0000, INT_STP_016_0001, INT_STP_016_0002,
 * scope=function}
 * @note Reference:
 */
stilib_result_t stilib_smu_start_state_check(void);
"""

    reader = SourceFileTraceabilityReader_C()

    info: SourceFileTraceabilityInfo = reader.read(
        input_string, file_path="foo.c"
    )

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 1
    assert info.markers[0].reqs == [
        "INT_STP_016_0000",
        "INT_STP_016_0001",
        "INT_STP_016_0002",
    ]

    assert info.markers[0].ng_source_line_begin == 11
    assert info.markers[0].ng_range_line_begin == 3
    assert info.markers[0].ng_range_line_end == 15
    assert info.markers[0].reqs_objs[0].ng_source_line == 11
    assert info.markers[0].reqs_objs[0].ng_source_column == 14
    assert info.markers[0].reqs_objs[1].ng_source_line == 11
    assert info.markers[0].reqs_objs[1].ng_source_column == 32
    assert info.markers[0].reqs_objs[2].ng_source_line == 11
    assert info.markers[0].reqs_objs[2].ng_source_column == 50


def test_20_node_fields():
    input_string = b"""\
#include <stdio.h>

/**
 * Some text.
 *
 * INTENTION: This
 *            is
 *            the
 *            intention.
 *
 * @relation(REQ-1, scope=function)
 */
void hello_world(void) {
    print("hello world\\n");
}
"""

    reader = SourceFileTraceabilityReader_C()

    info: SourceFileTraceabilityInfo = reader.read(
        input_string, file_path="foo.c"
    )

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 1
    assert info.markers[0].ng_source_line_begin == 11
    assert info.markers[0].ng_range_line_begin == 3
    assert info.markers[0].ng_range_line_end == 15
    assert info.markers[0].reqs_objs[0].ng_source_line == 11
    assert info.markers[0].reqs_objs[0].ng_source_column == 14


def test_90_edge_case_capitalized_field_with_colon_and_colon():
    """
    Ensure that there is no missing grammar token for a case reported by a user.

    Previously, StrictDoc would raise an exception related to Lark not finding
    a grammar token when parsing "L:LABEL: ..." kind of string (see below).
    This test makes sure that the parser works with no issues.

    https://github.com/strictdoc-project/strictdoc/issues/2342
    """

    input_string = b"""\
EFI_DEVICE_PATH *FileDevicePathFromConfig(EFI_HANDLE device,
					  CHAR16 *payloadpath)
{
    UINTN prefixlen = 0;
	   EFI_DEVICE_PATH *devpath = NULL;

	   LABELMODE lm = NOLABEL;
	   /* Check if payload path contains a
     * L:LABEL: item to specify a FAT partition or a
	    * C:LABEL: to specify a custom labeled FAT partition */
    if (StrnCmp(payloadpath, L"L:", 2) == 0) {
        lm = DOSFSLABEL;
    } else if (StrnCmp(payloadpath, L"C:", 2) == 0) {
		      lm = CUSTOMLABEL;
	   }
	   // ... truncated ...
}
"""

    reader = SourceFileTraceabilityReader_C()

    info: SourceFileTraceabilityInfo = reader.read(
        input_string, file_path="foo.c"
    )

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 0


def test_91_edge_case_capitalized_field_with_relation_marker():
    """
    Ensures that "@relation:" is not treated as an incomplete StrictDoc marker.

    Reduced fragment from this source file:
    https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/cpufreq/cpufreq-nforce2.c#n241

    https://github.com/strictdoc-project/strictdoc/issues/2342
    """

    input_string = b"""\
/**
 * nforce2_target - set a new CPUFreq policy
 * @policy: new policy
 * @target_freq: the target frequency
 * @relation: how that frequency relates to achieved frequency
 *  (CPUFREQ_RELATION_L or CPUFREQ_RELATION_H)
 *
 * Sets a new CPUFreq policy.
 */
static int nforce2_target(struct cpufreq_policy *policy,
			  unsigned int target_freq, unsigned int relation)
{
}
"""

    reader = SourceFileTraceabilityReader_C()

    info: SourceFileTraceabilityInfo = reader.read(
        input_string, file_path="foo.c"
    )

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 0


def test_92_edge_case_capitalized_letters():
    """
    Ensure that fragments such as "IP_VS_SCTP_S_COOKIE_REPLIED: C:COOKIE-ECHO"
    do not trigger parsing errors.

    Reduced fragment from this source file:
    https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/net/netfilter/ipvs/ip_vs_proto_sctp.c#n247

    https://github.com/strictdoc-project/strictdoc/issues/2342
    """

    input_string = b"""\
/*
 * IP_VS_SCTP_S_COOKIE_REPLIED: C:COOKIE-ECHO sent, wait for S:COOKIE-ACK
 */
void foobar(void) {}
"""

    reader = SourceFileTraceabilityReader_C()

    info: SourceFileTraceabilityInfo = reader.read(
        input_string, file_path="foo.c"
    )

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 0


def test_93_edge_case_capitalized_letters():
    """
    Ensure that fragments like "A: VMRUN:" do not trigger parsing errors.

    Reduced fragment from this source file:
    https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/arch/x86/kvm/svm/sev.c#n4532

    https://github.com/strictdoc-project/strictdoc/issues/2342
    """

    input_string = b"""\
void sev_es_prepare_switch_to_guest(struct vcpu_svm *svm, struct sev_es_save_area *hostsa)
{
    struct kvm *kvm = svm->vcpu.kvm;

    /*
     * All host state for SEV-ES guests is categorized into three swap types
     * based on how it is handled by hardware during a world switch:
     *
     * A: VMRUN:   Host state saved in host save area
     */
}
"""

    reader = SourceFileTraceabilityReader_C()

    info: SourceFileTraceabilityInfo = reader.read(
        input_string, file_path="foo.c"
    )

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 0


def test_94_edge_case_field_name_then_newline_then_field_value():
    r"""
    Ensure that fragments with <field name>\n<field value...> do not trigger
    parsing errors.

    Reduced fragment from this source file:
    https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/video/fbdev/i810/i810_gtf.c#n115

    https://github.com/strictdoc-project/strictdoc/issues/2342
    """

    input_string = b"""\
/**
 * i810fb_encode_registers - encode @var to hardware register values
 * @var: pointer to var structure
 * @par: pointer to hardware par structure
 *
 * DESCRIPTION:
 * Timing values in @var will be converted to appropriate
 * register values of @par.
 */
void foobar(void) {}
"""

    reader = SourceFileTraceabilityReader_C()

    info: SourceFileTraceabilityInfo = reader.read(
        input_string, file_path="foo.c"
    )

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 0
    assert len(info.source_nodes) == 1


def test_95_namespace_with_function():
    r"""
    Ensure that namespace is parsed correctly for free functions.
    """
    input_string = b"""\
namespace math {

int add(int a, int b) {
    return a + b;
}
}
"""
    reader = SourceFileTraceabilityReader_C()

    info: SourceFileTraceabilityInfo = reader.read(
        input_string, file_path="foo.cpp"
    )

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 0
    assert len(info.functions) == 1
    assert len(info.source_nodes) == 0

    assert info.functions[0].name == "math::add(int a, int b)"


def test_96_namespace_with_class_function():
    r"""
    Ensure that namespace is parsed correctly for class member functions.
    """
    input_string = b"""\
namespace math {

class Adder {
public:
int add(int a, int b) {
    return a + b;
}
};
}
"""
    reader = SourceFileTraceabilityReader_C()

    info: SourceFileTraceabilityInfo = reader.read(
        input_string, file_path="foo.cpp"
    )

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 0
    assert len(info.functions) == 1
    assert len(info.source_nodes) == 0

    assert info.functions[0].name == "math::Adder::add(int a, int b)"


def test_97_multiline_function():
    r"""
    Ensure functions defined on multiple lines due to linting
    tools are parsed correctly. The saved name should not have any
    extra spaces, or newline characters.

    """
    input_string = b"""\
int add(int a,
    int b) {
    return a + b;
}
"""
    reader = SourceFileTraceabilityReader_C()

    info: SourceFileTraceabilityInfo = reader.read(
        input_string, file_path="foo.cpp"
    )

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 0
    assert len(info.functions) == 1
    assert len(info.source_nodes) == 0

    assert info.functions[0].name == "add(int a, int b)"


def test_100_known_c_macro_zephyr_test():
    """
    Ensure that Zephyr's function-like test macro is recognized as a
    function with its full macro invocation as the display name.
    """

    input_string = b"""\
ZTEST_USER(semaphore, test_k_sem_correct_count_limit)
{
  // Some code here...
}
"""
    reader = SourceFileTraceabilityReader_C()

    info: SourceFileTraceabilityInfo = reader.read(
        input_string, file_path="foo.cpp"
    )

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 0
    assert len(info.functions) == 1
    assert len(info.source_nodes) == 0

    assert (
        info.functions[0].name
        == "ZTEST_USER(semaphore, test_k_sem_correct_count_limit)"
    )
    assert (
        info.functions[0].display_name
        == "ZTEST_USER(semaphore, test_k_sem_correct_count_limit)"
    )


def test_101_known_c_macro_zephyr_test_with_comment():
    """
    Ensure that Zephyr's function-like test macro is recognized as a
    function with its full macro invocation as the display name.
    """

    input_string = b"""\
/*
 * Copyright (c) 2016, 2020 Intel Corporation
 *
 * SPDX-License-Identifier: Apache-2.0
 */


/**
 * @brief Test the max value a semaphore can be given and taken
 * @details
 * - Reset an initialized semaphore's count to zero.
 * - Give the semaphore by a thread and verify the semaphore's count is
 *   as expected.
 * - Verify the max count a semaphore can reach.
 * - Take the semaphore by a thread and verify the semaphore's count is
 *   as expected.
 * - Verify the max times a semaphore can be taken.
 * @ingroup kernel_semaphore_tests
 * @see k_sem_count_get(), k_sem_give()
 */
ZTEST_USER(semaphore, test_k_sem_correct_count_limit)
{

	/* reset an initialized semaphore's count to zero */
	k_sem_reset(&simple_sem);
	expect_k_sem_count_get(&simple_sem, 0U, "k_sem_reset failed: %u != %u");

	/* Give the semaphore by a thread and verify the semaphore's
	 * count is as expected
	 */
	for (int i = 1; i <= SEM_MAX_VAL; i++) {
		k_sem_give(&simple_sem);
		expect_k_sem_count_get_nomsg(&simple_sem, i);
	}

	/* Verify the max count a semaphore can reach
	 * continue to run k_sem_give,
	 * the count of simple_sem will not increase anymore
	 */
	for (int i = 0; i < 5; i++) {
		k_sem_give(&simple_sem);
		expect_k_sem_count_get_nomsg(&simple_sem, SEM_MAX_VAL);
	}

	/* Take the semaphore by a thread and verify the semaphore's
	 * count is as expected
	 */
	for (int i = SEM_MAX_VAL - 1; i >= 0; i--) {
		expect_k_sem_take_nomsg(&simple_sem, K_NO_WAIT, 0);
		expect_k_sem_count_get_nomsg(&simple_sem, i);
	}

	/* Verify the max times a semaphore can be taken
	 * continue to run k_sem_take, simple_sem can not be taken and
	 * it's count will be zero
	 */
	for (int i = 0; i < 5; i++) {
		expect_k_sem_take_nomsg(&simple_sem, K_NO_WAIT, -EBUSY);

		expect_k_sem_count_get_nomsg(&simple_sem, 0U);
	}
}
"""
    reader = SourceFileTraceabilityReader_C()

    info: SourceFileTraceabilityInfo = reader.read(
        input_string, file_path="foo.cpp"
    )

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 0
    assert len(info.functions) == 1
    assert len(info.source_nodes) == 1

    assert (
        info.functions[0].name
        == "ZTEST_USER(semaphore, test_k_sem_correct_count_limit)"
    )
    assert (
        info.functions[0].display_name
        == "ZTEST_USER(semaphore, test_k_sem_correct_count_limit)"
    )


def test_102_known_c_macro_linux_syscall_define():
    input_string = b"""\
SYSCALL_DEFINE2(clock_gettime, const clockid_t, which_clock,
                struct __kernel_timespec __user *, tp)
{
    // ...
    return error;
}
"""
    reader = SourceFileTraceabilityReader_C()

    info: SourceFileTraceabilityInfo = reader.read(
        input_string, file_path="foo.cpp"
    )

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 0
    assert len(info.functions) == 1
    assert len(info.source_nodes) == 0

    expected_function_name = (
        "SYSCALL_DEFINE2(clock_gettime, "
        "const clockid_t, which_clock, struct __kernel_timespec __user *, tp"
        ")"
    )

    assert info.functions[0].name == expected_function_name
    assert info.functions[0].display_name == expected_function_name


def test_103_error_recovery_linux_define_per_cpu_macro():
    """
    Ensure this snippet derived from Linux kernel/softirq.c doesn't drive the
    C reader into NotImplementedError. DEFINE_PER_CPU expectedly confuses the
    parser. The rest of the snippet is special context that triggered undefined
    behavior manifesting as NotImplemented error in StrictDoc <= 0.22.0a1.
    """
    input_string = b"""\
static DEFINE_PER_CPU(struct softirq_ctrl, softirq_ctrl) = {
	.lock	= INIT_LOCAL_LOCK(softirq_ctrl.lock),
};

struct lockdep_map bh_lock_map = {
	.name			= "local_bh",
};

static void handle_softirqs()
{
	foo("\\n", bar());
	if (pending) { }
}
"""
    reader = SourceFileTraceabilityReader_C()

    # must not raise NotImplementedError
    assert reader.read(input_string, file_path="foo.cpp")
