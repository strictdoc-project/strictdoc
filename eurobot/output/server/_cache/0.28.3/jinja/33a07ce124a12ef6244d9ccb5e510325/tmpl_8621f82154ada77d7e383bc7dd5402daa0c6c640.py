from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/table/root_node.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_doc_mid = l_0_document_config = l_0_document_version_ = l_0_document_date_ = missing
    try:
        t_1 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    yield '\n\n\n'
    l_0_doc_mid = environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'), 'reserved_mid')
    context.vars['doc_mid'] = l_0_doc_mid
    context.exported_vars.add('doc_mid')
    l_0_document_config = environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'), 'config')
    context.vars['document_config'] = l_0_document_config
    context.exported_vars.add('document_config')
    l_0_document_version_ = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_document_version'))
    context.vars['document_version_'] = l_0_document_version_
    context.exported_vars.add('document_version_')
    l_0_document_date_ = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_document_date'))
    context.vars['document_date_'] = l_0_document_date_
    context.exported_vars.add('document_date_')
    yield '<sdoc-node>\n  <h1 data-testid="document-title">'
    l_1_field_content = environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'), 'title')
    l_1_document_title_wrap = True
    pass
    template = environment.get_template('screens/document/table/field_display_mode/document_title.jinja', 'screens/document/table/root_node.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'document_title_wrap': l_1_document_title_wrap, 'field_content': l_1_field_content, 'doc_mid': l_0_doc_mid, 'document_config': l_0_document_config, 'document_date_': l_0_document_date_, 'document_version_': l_0_document_version_}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_field_content = l_1_document_title_wrap = missing
    l_1_local_anchor = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_local_anchor'), environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'))
    pass
    template = environment.get_template('components/anchor_document/index.jinja', 'screens/document/table/root_node.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'local_anchor': l_1_local_anchor, 'doc_mid': l_0_doc_mid, 'document_config': l_0_document_config, 'document_date_': l_0_document_date_, 'document_version_': l_0_document_version_}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_local_anchor = missing
    yield '\n  </h1>\n\n  '
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_issues'), environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document')))
    yield '\n\n  <sdoc-meta>\n    '
    l_1_field_content = environment.getattr((undefined(name='document_config') if l_0_document_config is missing else l_0_document_config), 'uid')
    l_1_field_label = 'UID'
    l_1_field_name = 'UID'
    l_1_field_testid = 'uid'
    pass
    template = environment.get_template('screens/document/table/field_display_mode/document_config_field.jinja', 'screens/document/table/root_node.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_1_field_content, 'field_label': l_1_field_label, 'field_name': l_1_field_name, 'field_testid': l_1_field_testid, 'doc_mid': l_0_doc_mid, 'document_config': l_0_document_config, 'document_date_': l_0_document_date_, 'document_version_': l_0_document_version_}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_field_content = l_1_field_label = l_1_field_name = l_1_field_testid = missing
    l_1_field_content = (undefined(name='document_version_') if l_0_document_version_ is missing else l_0_document_version_)
    l_1_field_label = 'VERSION'
    l_1_field_name = 'VERSION'
    l_1_field_testid = 'version'
    pass
    template = environment.get_template('screens/document/table/field_display_mode/document_config_field.jinja', 'screens/document/table/root_node.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_1_field_content, 'field_label': l_1_field_label, 'field_name': l_1_field_name, 'field_testid': l_1_field_testid, 'doc_mid': l_0_doc_mid, 'document_config': l_0_document_config, 'document_date_': l_0_document_date_, 'document_version_': l_0_document_version_}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_field_content = l_1_field_label = l_1_field_name = l_1_field_testid = missing
    if (not t_1((undefined(name='document_date_') if l_0_document_date_ is missing else l_0_document_date_))):
        pass
        l_1_field_content = (undefined(name='document_date_') if l_0_document_date_ is missing else l_0_document_date_)
        l_1_field_label = 'DATE'
        l_1_field_name = 'DATE'
        l_1_field_testid = 'date'
        pass
        template = environment.get_template('screens/document/table/field_display_mode/document_meta_readonly_field.jinja', 'screens/document/table/root_node.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_1_field_content, 'field_label': l_1_field_label, 'field_name': l_1_field_name, 'field_testid': l_1_field_testid, 'doc_mid': l_0_doc_mid, 'document_config': l_0_document_config, 'document_date_': l_0_document_date_, 'document_version_': l_0_document_version_}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_field_content = l_1_field_label = l_1_field_name = l_1_field_testid = missing
    l_1_field_content = environment.getattr((undefined(name='document_config') if l_0_document_config is missing else l_0_document_config), 'classification')
    l_1_field_label = 'CLASSIFICATION'
    l_1_field_name = 'CLASSIFICATION'
    l_1_field_testid = 'classification'
    pass
    template = environment.get_template('screens/document/table/field_display_mode/document_config_field.jinja', 'screens/document/table/root_node.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_1_field_content, 'field_label': l_1_field_label, 'field_name': l_1_field_name, 'field_testid': l_1_field_testid, 'doc_mid': l_0_doc_mid, 'document_config': l_0_document_config, 'document_date_': l_0_document_date_, 'document_version_': l_0_document_version_}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_field_content = l_1_field_label = l_1_field_name = l_1_field_testid = missing
    l_1_field_content = environment.getattr((undefined(name='document_config') if l_0_document_config is missing else l_0_document_config), 'requirement_prefix')
    l_1_field_label = 'PREFIX'
    l_1_field_name = 'PREFIX'
    l_1_field_testid = 'prefix'
    pass
    template = environment.get_template('screens/document/table/field_display_mode/document_config_field.jinja', 'screens/document/table/root_node.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'field_content': l_1_field_content, 'field_label': l_1_field_label, 'field_name': l_1_field_name, 'field_testid': l_1_field_testid, 'doc_mid': l_0_doc_mid, 'document_config': l_0_document_config, 'document_date_': l_0_document_date_, 'document_version_': l_0_document_version_}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_field_content = l_1_field_label = l_1_field_name = l_1_field_testid = missing
    template = environment.get_template('screens/document/table/field_display_mode/document_custom_meta.jinja', 'screens/document/table/root_node.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'doc_mid': l_0_doc_mid, 'document_config': l_0_document_config, 'document_date_': l_0_document_date_, 'document_version_': l_0_document_version_}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '</sdoc-meta>\n\n</sdoc-node>'

blocks = {}
debug_info = '6=20&7=23&8=26&9=29&16=36&19=45&23=53&33=60&43=72&47=79&54=86&65=98&75=110&79=117'