def render_turbo_stream(content: str, action: str, target: str):
    assert action in ("append", "update")
    turbo_stream = f"""
<turbo-stream action="{action}" target="{target}">
  <template>
    {content}
  </template>
</turbo-stream>
"""
    return turbo_stream
