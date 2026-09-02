from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/tips.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    pass
    yield '<turbo-frame data-js-modal>\n  <sdoc-backdrop>\n    <sdoc-modal>\n      <sdoc-modal-container data-testid="table-tips-content">\n        <h3>TABLE screen tips</h3>\n        <p><b>Filter view</b></p>\n        <ul>\n          <li>Use the <strong>Columns</strong> panel to show or hide individual fields in the table.</li>\n          <li>Use the <strong>Nodes</strong> panel to filter which node types are displayed in the table.</li>\n        </ul>\n        <p><b>Edit mode</b></p>\n        <ul>\n          <li>Enable <b>Edit mode</b> to edit document content directly in the table.</li>\n          <li>Click a field to edit it. Save with <code>Ctrl/Cmd+Enter</code> or by <i>leaving the field</i>. Press <code>Escape</code> to cancel without changes.</li>\n          <li>Use <b>Add</b> separators between rows to create new nodes.</li>\n          <li>Use the <b>Delete</b> action in the <code>Type</code> column to remove nodes.</li>\n          <li><b>Add Node</b> is unavailable while sorting or row filtering is active.</li>\n        </ul>\n        <p><b>Pan the page</b></p>\n        <ul>\n          <li>Hold <code>Space</code> and drag to move around the table.</li>\n          <li>While editing a text field, <code>Space</code> inserts a space character instead of activating pan mode.</li>\n        </ul>\n\n      </sdoc-modal-container>'
    l_1_cancel_name = 'Close'
    pass
    template = environment.get_template('components/button/cancel.jinja', 'screens/document/table/tips.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'cancel_name': l_1_cancel_name}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_cancel_name = missing
    yield '</sdoc-modal>\n  </sdoc-backdrop>\n</turbo-frame>'

blocks = {}
debug_info = '27=14'