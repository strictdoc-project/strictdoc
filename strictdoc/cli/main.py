from strictdoc.backend.rst import dump

somerst = """
Friendly lists
--------------

.. aws-meta::
    :types: List
    :keywords: Safety, Resilience

    `resilience-engineering <https://github.com/lorin/resilience-engineering>`_

    Resilience engineering papers http://resiliencepapers.club
"""

dump(somerst)
