from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'websocket.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    pass
    if environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_running_on_server'):
        pass
        yield '\n<sdoc-toast id="connection_status"></sdoc-toast>\n\n<script>\n  var clientId = Date.now();\n  var ws_protocol = window.location.protocol === \'https:\' ? \'wss:\' : \'ws:\';\n  var ws = new WebSocket(`${ws_protocol}//${window.location.host}/ws/${clientId}`);\n  ws.onmessage = function(event) {\n    if (event.data === "reload") {\n      window.location.reload();\n    } else if (event.data.indexOf("error:") === 0) {\n      document.getElementById("connection_status").innerHTML = `\n        Document build failed. Fix the source files and save again.\n        <pre style="white-space: pre-wrap;">${event.data.slice("error:".length)}</pre>\n      `;\n    }\n  };\n  ws.onopen = function(e) {\n    // Nothing just yet.\n  }\n  ws.onclose = function(e) {\n    document.getElementById("connection_status").innerHTML = `\n      Connection with the server is lost.\n      <a href="#" onclick="location.reload(); return false;">Click to reload</a>\n    `;\n  };\n  window.onbeforeunload = function (e) {\n    // Suprisingly, the last milleseconds of the page lifecycle let the page\n    // still update its HTML which creates a visual artefact when refreshing the\n    // page in the browser continuously.\n    // This event ensures that we disable websockets when the page is about to\n    // be refreshed/left.\n    ws.onclose = null;\n  };\n\n</script>'

blocks = {}
debug_info = '1=12'