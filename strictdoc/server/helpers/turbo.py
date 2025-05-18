from markupsafe import Markup


def render_turbo_stream(content: str, action: str, target: str) -> Markup:
    assert action in ("append", "replace", "update")

    turbo_stream = f"""
<turbo-stream action="{action}" target="{target}">
  <template>
    {content}
  </template>
</turbo-stream>
"""
    return Markup(turbo_stream)
