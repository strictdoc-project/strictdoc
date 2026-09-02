from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/filter.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    pass
    yield '<div class="table-toolbar" data-testid="table-toolbar">\n  <div class="table-toolbar__dock">\n  <div class="table-toolbar__sort-reset" hidden>\n    <button class="table-toolbar__btn action_button"\n            data-testid="table-toolbar-sort-reset">\n            <span class="table-toolbar__btn-text">Reset sort</span></button>\n  </div>'
    if environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'is_running_on_server'):
        pass
        yield '<div class="table-toolbar__edit">\n    <button class="table-toolbar__btn table-toolbar__btn--edit action_button"\n            aria-pressed="false"\n            js-table_view_edit-toggle\n            data-testid="table-toolbar-edit-btn">'
        template = environment.get_template('icons/ico16_edit.svg', 'screens/document/table/filter.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '<span class="table-toolbar__btn-text">Edit</span></button>\n  </div>'
    yield '<div class="table-toolbar__columns">\n    <button class="table-toolbar__btn action_button"\n            aria-haspopup="true"\n            aria-expanded="false"\n            data-label="Columns"\n            data-testid="table-toolbar-columns-btn">'
    template = environment.get_template('icons/ico16_dropdown_collapse.svg', 'screens/document/table/filter.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '<span class="table-toolbar__btn-text">Columns<span class="table-toolbar__btn-info"></span></span>\n    </button>\n    <div class="table-toolbar__dropdown dropdown_menu"\n          hidden\n          aria-hidden="true"\n          role="dialog"\n          aria-label="Column visibility"\n          data-testid="table-toolbar-columns-panel">\n      <div class="table-toolbar__dropdown-header">\n        <span class="table-toolbar__dropdown-title">Visible:</span>\n        <button class="table-toolbar__reset compact action_button"\n                data-testid="table-toolbar-columns-reset">Show all</button>\n      </div>\n      <ul class="table-toolbar__list" data-testid="table-toolbar-columns-list"></ul>\n    </div>\n  </div>\n  <div class="table-toolbar__rows">\n    <button class="table-toolbar__btn action_button"\n            aria-haspopup="true"\n            aria-expanded="false"\n            data-testid="table-toolbar-rows-btn">'
    template = environment.get_template('icons/ico16_dropdown_collapse.svg', 'screens/document/table/filter.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '<span class="table-toolbar__btn-text">Nodes<span class="table-toolbar__btn-info"></span></span>\n    </button>\n    <div class="table-toolbar__dropdown dropdown_menu"\n          hidden\n          aria-hidden="true"\n          role="dialog"\n          aria-label="Row visibility"\n          data-testid="table-toolbar-rows-panel">\n      <div class="table-toolbar__dropdown-header">\n        <span class="table-toolbar__dropdown-title">Visible:</span>\n        <button class="table-toolbar__reset compact action_button"\n                data-testid="table-toolbar-rows-reset">Show all</button>\n      </div>\n      <ul class="table-toolbar__list" data-testid="table-toolbar-rows-list"></ul>\n    </div>\n    </div>\n    <div class="table-toolbar__tips">\n      <button class="table-toolbar__btn action_button"\n              data-testid="table-toolbar-tips-btn">\n              <span class="table-toolbar__btn-text">?</span></button>\n    </div>\n  </div>\n</div>\n'
    template = environment.get_template('components/checkbox/index.jinja', 'screens/document/table/filter.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '<template id="table-tips-modal-template">'
    template = environment.get_template('screens/document/table/tips.jinja', 'screens/document/table/filter.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</template>\n<script>\ndocument.addEventListener(\'DOMContentLoaded\', function() {\n  document.querySelector(\'[data-testid="table-toolbar-tips-btn"]\').addEventListener(\'click\', function() {\n    var template = document.getElementById(\'table-tips-modal-template\');\n    document.getElementById(\'modal\').innerHTML = template.innerHTML;\n  });\n});\n</script>'

blocks = {}
debug_info = '8=13&14=16&24=24&46=31&71=38&74=45'