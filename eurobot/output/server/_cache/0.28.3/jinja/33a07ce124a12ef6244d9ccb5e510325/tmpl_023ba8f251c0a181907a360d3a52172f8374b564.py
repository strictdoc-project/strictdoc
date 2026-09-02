from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/main.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_column_labels = l_0_content_entries = missing
    try:
        t_1 = environment.filters['list']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'list' found.")
    pass
    yield '\n  <div class="main"\n       js-pan_with_space="true"\n       js-table_view_edit\n  >\n    '
    template = environment.get_template('_shared/tags.jinja.html', 'screens/document/table/main.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'column_labels': l_0_column_labels, 'content_entries': l_0_content_entries}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n      <div class="content" js-toc_highlighting-content_root>\n        <div id="table-add-node-feedback" hidden></div>\n\n        \n        \n        \n        \n        '
    template = environment.get_template('screens/document/table/root_node.jinja', 'screens/document/table/main.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'column_labels': l_0_column_labels, 'content_entries': l_0_content_entries}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n\n        \n        \n        \n        '
    l_0_column_labels = {'RELATIONS': 'REFS', 'TITLE': 'Title', 'STATEMENT': 'Statement', 'RATIONALE': 'Rationale', 'COMMENT': 'Comment'}
    context.vars['column_labels'] = l_0_column_labels
    context.exported_vars.add('column_labels')
    l_0_content_entries = t_1(context.eval_ctx, context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document_content_iterator')))
    context.vars['content_entries'] = l_0_content_entries
    context.exported_vars.add('content_entries')
    yield '<table class="content-view-table" js-table_view_edit-table>\n\n          \n          <thead class="content-view-table_sticky-header">\n            <tr>\n              <th class="content-view-th" data-testid="col-header-Type">\n                <div class="content-view-th__content">\n                  <span class="content-view-th__label">Type</span>\n                  <button class="content-view-th__sort-btn" aria-label="Sort by Type">'
    template = environment.get_template('icons/ico16_sort.svg', 'screens/document/table/main.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'column_labels': l_0_column_labels, 'content_entries': l_0_content_entries}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</button>\n                </div>\n              </th>\n              <th class="content-view-th" data-testid="col-header-Level">\n                <div class="content-view-th__content">\n                  <span class="content-view-th__label">Level</span>\n                  <button class="content-view-th__sort-btn" aria-label="Sort by Level">'
    template = environment.get_template('icons/ico16_sort.svg', 'screens/document/table/main.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'column_labels': l_0_column_labels, 'content_entries': l_0_content_entries}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</button>\n                </div>\n              </th>'
    for l_1_column in context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'enumerate_table_columns')):
        l_1_col_label = missing
        _loop_vars = {}
        pass
        l_1_col_label = context.call(environment.getattr((undefined(name='column_labels') if l_0_column_labels is missing else l_0_column_labels), 'get'), l_1_column, l_1_column, _loop_vars=_loop_vars)
        _loop_vars['col_label'] = l_1_col_label
        yield '<th class="content-view-th" data-testid="col-header-'
        yield escape((undefined(name='col_label') if l_1_col_label is missing else l_1_col_label))
        yield '">\n                  <div class="content-view-th__content">\n                    <span class="content-view-th__label">'
        yield escape((undefined(name='col_label') if l_1_col_label is missing else l_1_col_label))
        yield '</span>\n                    <button class="content-view-th__sort-btn" aria-label="Sort by '
        yield escape((undefined(name='col_label') if l_1_col_label is missing else l_1_col_label))
        yield '">'
        template = environment.get_template('icons/ico16_sort.svg', 'screens/document/table/main.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'col_label': l_1_col_label, 'column': l_1_column, 'column_labels': l_0_column_labels, 'content_entries': l_0_content_entries}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '</button>\n                  </div>\n                </th>'
    l_1_column = l_1_col_label = missing
    yield '</tr>\n          </thead>\n\n          \n          '
    template = environment.get_template('screens/document/table/body.jinja', 'screens/document/table/main.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'column_labels': l_0_column_labels, 'content_entries': l_0_content_entries}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n        </table>\n      </div>\n      \n  </div>\n  '

blocks = {}
debug_info = '78=20&86=27&95=34&102=37&111=41&117=48&120=55&121=59&122=62&124=64&125=66&133=77'