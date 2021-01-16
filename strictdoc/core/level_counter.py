class LevelCounter:
    def __init__(self):
        self.levels = []

    def adjust(self, level):
        current_level = len(self.levels)

        if current_level < level:
            self.levels.append(1)
        elif current_level > level:
            while len(self.levels) > level:
                self.levels.pop()

            self.levels[-1] += 1
        else:
            self.levels[-1] += 1

    def get_string(self):
        str_levels = map(lambda el: str(el), self.levels)
        string = ".".join(str_levels)

        return string
