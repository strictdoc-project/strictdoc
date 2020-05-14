from strictdoc.backend.rst import dump_ast, dump_pretty

somerst = """
AWESOME
=======

Friendly lists
--------------

.. aws-meta::
    :types: List
    :keywords: Safety, Resilience

    `resilience-engineering <https://github.com/lorin/resilience-engineering>`_

    Resilience engineering papers http://resiliencepapers.club

.. aws-meta::
    :types: List
    :keywords: Software Quality

    `awesome-software-quality <https://github.com/ligurio/awesome-software-quality>`_

    List of free software testing and verification resources

Resources
---------

.. aws-meta::
    :types: Resource
    :keywords: Standards
    :industries: Space
    :standards: ECSS

    `European Cooperation for Space Standardization <http://ecss.nl/>`_

"""

dump_ast(somerst)
dump_pretty(somerst)
