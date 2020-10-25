from collections import OrderedDict


class RSTParserSharedState:
    categories_spec = OrderedDict()

    @classmethod
    def reset(cls):
        RSTParserSharedState.categories_spec.clear()
