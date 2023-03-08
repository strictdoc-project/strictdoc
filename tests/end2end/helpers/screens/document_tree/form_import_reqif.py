from seleniumbase import BaseCase

from tests.end2end.helpers.screens.form.form import Form


class Form_ImportReqIF(Form):  # pylint: disable=invalid-name
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        super().__init__(test_case)

    def do_choose_file(self, path_to_reqif_sample) -> None:
        reqif_input_field = self.test_case.find_element(
            "//*[@data-testid='form-reqif_file-field']"
        )
        reqif_input_field.send_keys(path_to_reqif_sample)
