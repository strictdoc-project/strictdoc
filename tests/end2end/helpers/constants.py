# Using XPATH to search text containing &nbsp;
# https://stackoverflow.com/a/59699055
NBSP = "\u00A0"

# In the Document view, the content of the document is formed by a sequence of
# <sdoc-node> tags. Each <sdoc-node> tag represents either a Section,
# a Requirement or a document header. The first node in the sequence is always
# the <sdoc-node> of a document header which consists of document's
# title, config and abstract.

# The order number of the sdoc-node,
# which is actually the document header
# and outputs document title, config and abstract.
NODE_0 = 1

# The order number of the sdoc-node,
# which is actually the first node
# (section or requirement) on the page.
NODE_1 = 2

TEXT_WITH_TRAILING_WHITESPACES = """
Hello world!    
    
Hello world!    
    
Hello world!    
                """  # noqa: W291, W293
