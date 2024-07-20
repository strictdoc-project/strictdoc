from markupsafe import Markup


# mypy: disable-error-code="no-untyped-def"
def render_turbo_stream(content: str, action: str, target: str):
    assert action in ("append", "replace", "update")

    turbo_stream = f"""
<turbo-stream action="{action}" target="{target}">
  <template>
    {content}
  </template>
</turbo-stream>
"""
    return Markup(turbo_stream)
