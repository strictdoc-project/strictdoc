# mypy: disable-error-code="no-untyped-def"
import os

from docutils.parsers.rst.directives.images import Image


class WildcardEnhancedImage(Image):
    WILDCARD_EXTENSIONS = ["svg", "png", "gif", "jpg", "jpeg"]

    current_reference_path = os.getcwd()

    def run(self):
        # A user has suggested that StrictDoc could be capable of rendering
        # a Sphinx-specific directive: image.* (this directive does not exist
        # in the Docutils).
        # This directive allows a specification of "image.*", and the wildcard
        # extension is replaced by a search over a number of extensions.
        # We want StrictDoc to recognize this custom .* prefix and interpret
        # it with a search over a number of extensions. If a file with a given
        # extension is found, we pass it to the original Image directive, and
        # it works as normal.
        #
        # User request:
        # https://github.com/strictdoc-project/strictdoc/issues/1106
        # The Sphinx directive is documented here:
        # https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#images
        #
        # Sphinx/Docutils files with relevant implementation:
        # - docutils/docutils/parsers/rst/directives/images.py
        # - sphinx/writers/html5.py (visit_image)  # noqa: ERA001
        #
        # When this method is called from the RST string:
        # """
        # .. image:: some_picture.*
        # """,
        # the self.arguments looks like this:
        # ['some_picture.*']  # noqa: ERA001
        assert len(self.arguments) > 0
        rel_path_to_image = self.arguments[0]
        if rel_path_to_image.endswith(".*"):
            rel_path_to_image_no_wc = rel_path_to_image[:-2]
            for extension in WildcardEnhancedImage.WILDCARD_EXTENSIONS:
                rel_path_to_image_with_extension = (
                    rel_path_to_image_no_wc + "." + extension
                )
                full_path_to_image_with_extension = os.path.join(
                    WildcardEnhancedImage.current_reference_path,
                    rel_path_to_image_with_extension,
                )
                if os.path.exists(full_path_to_image_with_extension):
                    # We have found a matching file, let's use it.
                    self.arguments[0] = os.path.join(
                        rel_path_to_image_with_extension
                    )
                    break
            else:
                # If the argument is not provided, raise an error.
                error_message = (
                    f"No image could be found to match the wildcard: "
                    f"{rel_path_to_image}"
                )
                self.state_machine.reporter.error(
                    error_message, line=self.lineno
                )
                # Return an empty list of nodes to stop the rendering
                # process.
                return []

        return super().run()
