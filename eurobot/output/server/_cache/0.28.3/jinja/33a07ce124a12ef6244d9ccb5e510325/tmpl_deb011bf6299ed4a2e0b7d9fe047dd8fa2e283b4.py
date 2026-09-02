from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/document/action_list.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    pass
    yield '<a\n  href="/actions/document/edit_grammar?document_mid='
    yield escape(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'), 'reserved_mid'))
    yield '"\n  class="dropdown_menu_item"\n  data-turbo="true"\n  data-turbo-action="replace"\n  title="Edit document grammar"\n  data-testid="document-edit-grammar-action"\n  role="menuitem"\n>'
    template = environment.get_template('icons/ico16_gear.svg', 'screens/document/document/action_list.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield ' Edit grammar</a>'
    if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_activated_html2pdf')):
        pass
        yield '<a\n  class="dropdown_menu_item"\n  href="/export_html2pdf/'
        yield escape(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'), 'reserved_mid'))
        yield '"\n  data-testid="document-export-html2pdf-action"\n  role="menuitem"\n>'
        template = environment.get_template('icons/ico16_export.svg', 'screens/document/document/action_list.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield ' Export to PDF</a>'
    if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_activated_reqif')):
        pass
        yield '<a\n  class="dropdown_menu_item"\n  href="/reqif/export_document/'
        yield escape(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'), 'reserved_mid'))
        yield '"\n  data-testid="document-export-reqif-action"\n  role="menuitem"\n>'
        template = environment.get_template('icons/ico16_export.svg', 'screens/document/document/action_list.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield ' Export to ReqIF</a>'
    yield '<a\n  class="dropdown_menu_item"\n  href="/actions/document/delete_document?document_mid='
    yield escape(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document'), 'reserved_mid'))
    yield '"\n  data-turbo="true"\n  data-turbo-method="delete"\n  title="Delete document"\n  data-testid="document-delete-action"\n  role="menuitem"\n>Delete document</a>'

blocks = {}
debug_info = '2=13&9=15&11=22&14=25&17=27&20=34&23=37&26=39&31=47'