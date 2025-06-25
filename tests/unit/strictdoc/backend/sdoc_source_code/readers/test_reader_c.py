import sys

import pytest

from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.reader_c import (
    SourceFileTraceabilityReader_C,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 9), reason="Requires Python 3.9 or higher"
)


def test_00_empty_file():
    input_string = b""""""

    reader = SourceFileTraceabilityReader_C()

    info = reader.read(input_string)

    assert isinstance(info, SourceFileTraceabilityInfo)
    assert len(info.markers) == 0


def test_01_single_string():
    input_string = b"""\
// Unimportant comment.
"""

    reader = SourceFileTraceabilityReader_C()

    info = reader.read(input_string)

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
