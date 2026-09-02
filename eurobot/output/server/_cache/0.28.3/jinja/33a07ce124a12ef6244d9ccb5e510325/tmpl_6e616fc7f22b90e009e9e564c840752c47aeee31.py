from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/diff_and_changelog/node/document.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_document = resolve('document')
    l_0_side = resolve('side')
    l_0_tab = resolve('tab')
    l_0_document_change = missing
    try:
        t_1 = environment.filters['safe']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'safe' found.")
    try:
        t_2 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    l_0_document_change = context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_stats'), 'find_change'), (undefined(name='document') if l_0_document is missing else l_0_document))
    context.vars['document_change'] = l_0_document_change
    context.exported_vars.add('document_change')
    yield '\n\n<details\n  class="diff_node"\n  '
    if (not t_2((undefined(name='document_change') if l_0_document_change is missing else l_0_document_change))):
        pass
        yield '\n    modified="'
        yield escape((undefined(name='side') if l_0_side is missing else l_0_side))
        yield '"\n  '
    yield '\n>\n  <summary>'
    l_1_badge_text = 'DOCUMENT (included)'
    pass
    template = environment.get_template('components/badge/index.jinja', 'features/diff_and_changelog/node/document.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'badge_text': l_1_badge_text, 'document_change': l_0_document_change}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_badge_text = missing
    yield '<span>\n      '
    yield escape((environment.getattr(environment.getattr((undefined(name='document') if l_0_document is missing else l_0_document), 'context'), 'title_number_string') if environment.getattr(environment.getattr((undefined(name='document') if l_0_document is missing else l_0_document), 'context'), 'title_number_string') else (Markup('&nbsp;') * ((environment.getattr(environment.getattr((undefined(name='document') if l_0_document is missing else l_0_document), 'context'), 'ng_level') * 2) - 1))))
    yield '\n    </span>\n    <span>'
    yield escape(environment.getattr((undefined(name='document') if l_0_document is missing else l_0_document), 'reserved_title'))
    yield '</span>'
    if ((undefined(name='tab') if l_0_tab is missing else l_0_tab) == 'diff'):
        pass
        if (not t_2((undefined(name='document_change') if l_0_document_change is missing else l_0_document_change))):
            pass
            if (not t_2(environment.getattr((undefined(name='document_change') if l_0_document_change is missing else l_0_document_change), 'document_token'))):
                pass
                l_1_uid = environment.getattr((undefined(name='document_change') if l_0_document_change is missing else l_0_document_change), 'document_token')
                pass
                template = environment.get_template('features/diff_and_changelog/sync/button.jinja', 'features/diff_and_changelog/node/document.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'uid': l_1_uid, 'document_change': l_0_document_change}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                l_1_uid = missing
    yield '</summary>\n\n  '
    template = environment.get_template('features/diff_and_changelog/fields/document_fields.jinja', 'features/diff_and_changelog/node/document.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'document_change': l_0_document_change}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n</details>'

blocks = {}
debug_info = '1=28&5=32&6=35&11=40&14=48&16=50&17=52&18=54&19=56&21=60&28=68'