import subprocess
import sys

if len(sys.argv) <= 2:
    print("error: expect_exit: expect arguments to be provided")
    exit(1)

expected_exit_code_arg = sys.argv[1]
try:
    expected_exit_code = int(expected_exit_code_arg)
    if expected_exit_code < 0 or expected_exit_code > 127:
        raise ValueError
except ValueError:
    print(
        "error: expect_exit: expect numeric exit code within range [0, 127]: {}".format(
            expected_exit_code_arg
        )
    )
    exit(1)

args = sys.argv.copy()

args.pop(0)
args.pop(0)

expect_no_content = False
if args[0] == "--expect-no-content":
    expect_no_content = True
    args.pop(0)

# To capture the output from the subprocess we set up stderr to be written to
# stdout. This ensures that we see the output from the subprocess in the same
# order as we do in a shell however this does not allow us to capture what is
# actually stdout and what is stderr.
process = subprocess.Popen(
    args,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

# How do I check if stdin has some data?
# https://stackoverflow.com/a/17735803/598057
# TODO: This is not a good idea. What if stdin is being piped in from a file?
# TODO: isatty() is telling you if stdin is coming in directly from a terminal,
# TODO: not if there is more data to read from stdin – Lathan Jul 24 '15 at 21:35
subprocess_input = sys.stdin.read() if not sys.stdin.isatty() else None
stdout, _ = process.communicate(input=subprocess_input)

unexpected_exit_code = process.returncode != expected_exit_code
if unexpected_exit_code:
    print(
        "error: expect_exit: expected exit code: {}, actual: {}".format(
            expected_exit_code, process.returncode
        )
    )

unexpected_content = expect_no_content and len(stdout) > 0
if unexpected_content:
    print("error: expect_exit: expected no content but received:")

output_lines = stdout.decode("utf-8").splitlines()
for word in output_lines:
    print(word)

if unexpected_exit_code or unexpected_content:
    exit(1)

exit(0)
