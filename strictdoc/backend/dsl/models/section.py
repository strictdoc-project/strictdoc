class SectionContext(object):
    def __init__(self):
        self.title_number_string = None


class Section(object):
    def __init__(self, parent, level, title, free_texts, section_contents):
        self.parent = parent
        self.level = int(level) if level else None
        self.title = title

        self.free_texts = free_texts
        self.section_contents = section_contents

        self.ng_level = None
        self.ng_sections = []
        self.ng_has_requirements = False
        self.context = SectionContext()

    def __str__(self):
        return f"Section(title: {self.title})"

    def __repr__(self):
        return self.__str__()

    @property
    def is_requirement(self):
        return False

    @property
    def is_section(self):
        return True


class FreeText:
    def __init__(self, parent, text):
        self.parent = parent
        self.text = text
        self.ng_level = None

    @property
    def is_requirement(self):
        return False

    @property
    def is_section(self):
        return False
