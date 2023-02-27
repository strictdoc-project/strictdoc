import difflib
import filecmp
import os.path
import shutil


class End2EndTestSetup:
    def __init__(self, path_to_test_file):
        assert os.path.isfile(path_to_test_file), path_to_test_file

        path_to_test_dir = os.path.dirname(os.path.abspath(path_to_test_file))
        assert os.path.isdir(path_to_test_dir), path_to_test_dir
        self.path_to_test_dir = path_to_test_dir

        # Input dir is where the inputs for the test are.
        # These contents are always copied to sandbox.
        self.path_to_input_dir = os.path.join(path_to_test_dir, "input")
        assert os.path.isdir(self.path_to_input_dir), self.path_to_input_dir

        # Expected output dir is where the test expectations are.
        # The expected output contents are compared with the contents of a
        # sandbox.
        self.path_to_expected_output_dir = os.path.join(
            path_to_test_dir, "expected_output"
        )
        assert os.path.isdir(
            self.path_to_expected_output_dir
        ), self.path_to_expected_output_dir

        # Sandbox is where the StrictDoc server will find its documents.
        self.path_to_sandbox = os.path.join(path_to_test_dir, ".sandbox")

        if os.path.isdir(self.path_to_sandbox):
            shutil.rmtree(self.path_to_sandbox)
        shutil.copytree(
            os.path.join(self.path_to_input_dir),
            os.path.join(self.path_to_sandbox),
        )

    def path_to_sandbox_file(self, file_name):
        path_to_sandbox_file = os.path.join(self.path_to_sandbox, file_name)
        assert os.path.isfile(path_to_sandbox_file), path_to_sandbox_file
        return path_to_sandbox_file

    def path_to_expected_output_dir_file(self, file_name):
        path_to_expected_output_dir_file = os.path.join(
            self.path_to_expected_output_dir, file_name
        )
        assert os.path.isfile(
            path_to_expected_output_dir_file
        ), path_to_expected_output_dir_file
        return path_to_expected_output_dir_file

    def compare_sandbox_and_expected_output(self):
        sandbox_files = End2EndTestSetup.find_files(self.path_to_sandbox)
        expected_files = End2EndTestSetup.find_files(
            self.path_to_expected_output_dir
        )
        diff_sandbox = [
            sandbox_file
            for sandbox_file in sandbox_files
            if sandbox_file not in expected_files
        ]
        diff_expected = [
            expected_file
            for expected_file in expected_files
            if expected_file not in sandbox_files
        ]
        if len(diff_sandbox) > 0 or len(diff_expected):
            raise AssertionError(
                f"Sandbox and expected output folders are not identical:\n"
                f"{self.path_to_sandbox}\n"
                f"{self.path_to_expected_output_dir}\n"
                "Diff:\n"
                f"Sandbox files that are not expected: {diff_sandbox}\n"
                f"Expected files that are not in sandbox: {diff_expected}\n"
            )
        for relative_path_to_sandbox_file in sandbox_files:
            path_to_sandbox_file = os.path.join(
                self.path_to_sandbox, relative_path_to_sandbox_file
            )
            path_to_expected_file = os.path.join(
                self.path_to_expected_output_dir, relative_path_to_sandbox_file
            )
            if not filecmp.cmp(path_to_sandbox_file, path_to_expected_file):
                diff = End2EndTestSetup.get_diff(
                    path_to_sandbox_file, path_to_expected_file
                )
                raise AssertionError(
                    f"Sandbox and expected output folders are not identical:\n"
                    f"{self.path_to_sandbox}\n"
                    f"{self.path_to_expected_output_dir}\n"
                    "Diff:\n"
                    f"{diff}"
                )
        return True

    @staticmethod
    def find_files(path_to_dir):
        assert os.path.isdir(path_to_dir), path_to_dir
        matches = []
        for root, _, filenames in os.walk(path_to_dir, topdown=True):
            for filename in filenames:
                relative_path = os.path.relpath(
                    os.path.join(root, filename), start=path_to_dir
                )
                matches.append(relative_path)
        return matches

    @staticmethod
    def get_diff(path_to_file1, path_to_file2):
        with open(path_to_file1, encoding="utf8") as file1:
            lines1 = file1.readlines()
        with open(path_to_file2, encoding="utf8") as file2:
            lines2 = file2.readlines()
        diff_result = "".join(
            difflib.unified_diff(
                lines1,
                lines2,
                fromfile=path_to_file1,
                tofile=path_to_file2,
                lineterm="",
            )
        )
        return diff_result
