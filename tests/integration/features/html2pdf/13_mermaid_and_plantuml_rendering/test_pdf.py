"""
@relation(SDOC-SRS-51, scope=file)
"""

from pypdf import PdfReader

reader = PdfReader("Output/html2pdf/pdf/input.pdf")

assert len(reader.pages) == 2, reader.pages

diagrams_page_text = reader.pages[1].extract_text()

# The Mermaid diagram must be rendered to an SVG in place: its node labels
# are visible as text, and its raw diagram source is gone.
assert "Start" in diagrams_page_text, diagrams_page_text
assert "End" in diagrams_page_text, diagrams_page_text
assert "graph TD" not in diagrams_page_text, diagrams_page_text

# The PlantUML diagram must be rendered to an SVG in place: its actor/
# message labels are visible as text, and its raw diagram source is gone.
assert "Alice" in diagrams_page_text, diagrams_page_text
assert "Bob" in diagrams_page_text, diagrams_page_text
assert "Hello" in diagrams_page_text, diagrams_page_text
assert "@startuml" not in diagrams_page_text, diagrams_page_text
assert "@enduml" not in diagrams_page_text, diagrams_page_text
