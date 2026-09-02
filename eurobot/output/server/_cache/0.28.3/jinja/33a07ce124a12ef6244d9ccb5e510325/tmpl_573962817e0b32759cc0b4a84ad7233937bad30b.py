from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/diff_and_changelog/fields/document_fields.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_document = resolve('document')
    l_0_view_object = resolve('view_object')
    l_0_uid_modified = resolve('uid_modified')
    l_0_side = resolve('side')
    l_0_colored_diff = resolve('colored_diff')
    l_0_node = l_0_document_change = l_0_title_modified = missing
    try:
        t_1 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    l_0_node = (undefined(name='document') if l_0_document is missing else l_0_document)
    context.vars['node'] = l_0_node
    context.exported_vars.add('node')
    yield '\n'
    l_0_document_change = context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_stats'), 'find_change'), (undefined(name='document') if l_0_document is missing else l_0_document))
    context.vars['document_change'] = l_0_document_change
    context.exported_vars.add('document_change')
    yield '\n\n<div class="diff_node_fields">\n\n\n'
    if environment.getattr((undefined(name='document') if l_0_document is missing else l_0_document), 'mid_permanent'):
        pass
        yield '\n  <div\n    class="diff_node_field"\n  >'
        l_1_badge_text = 'MID'
        pass
        template = environment.get_template('components/badge/index.jinja', 'features/diff_and_changelog/fields/document_fields.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'badge_text': l_1_badge_text, 'colored_diff': l_0_colored_diff, 'document_change': l_0_document_change, 'node': l_0_node, 'title_modified': l_0_title_modified, 'uid_modified': l_0_uid_modified}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_badge_text = missing
        yield '<span class="sdoc_pre_content">'
        yield escape(environment.getattr((undefined(name='document') if l_0_document is missing else l_0_document), 'reserved_mid'))
        yield '</span>\n  </div>\n'
    yield '\n\n'
    if (not t_1(environment.getattr((undefined(name='document') if l_0_document is missing else l_0_document), 'reserved_uid'))):
        pass
        yield '\n'
        l_0_uid_modified = (((not t_1(environment.getattr((undefined(name='document') if l_0_document is missing else l_0_document), 'reserved_uid'))) and (not t_1((undefined(name='document_change') if l_0_document_change is missing else l_0_document_change)))) and environment.getattr((undefined(name='document_change') if l_0_document_change is missing else l_0_document_change), 'uid_modified'))
        context.vars['uid_modified'] = l_0_uid_modified
        context.exported_vars.add('uid_modified')
        yield '\n<div\n  class="diff_node_field"\n  '
        if (undefined(name='uid_modified') if l_0_uid_modified is missing else l_0_uid_modified):
            pass
            yield '\n  modified="'
            yield escape((undefined(name='side') if l_0_side is missing else l_0_side))
            yield '"\n  '
        yield '\n>'
        l_1_badge_text = 'uid'
        pass
        template = environment.get_template('components/badge/index.jinja', 'features/diff_and_changelog/fields/document_fields.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'badge_text': l_1_badge_text, 'colored_diff': l_0_colored_diff, 'document_change': l_0_document_change, 'node': l_0_node, 'title_modified': l_0_title_modified, 'uid_modified': l_0_uid_modified}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        l_1_badge_text = missing
        if (undefined(name='uid_modified') if l_0_uid_modified is missing else l_0_uid_modified):
            pass
            l_0_colored_diff = context.call(environment.getattr((undefined(name='document_change') if l_0_document_change is missing else l_0_document_change), 'get_colored_uid_diff'), (undefined(name='side') if l_0_side is missing else l_0_side))
            context.vars['colored_diff'] = l_0_colored_diff
            context.exported_vars.add('colored_diff')
            if (not t_1((undefined(name='colored_diff') if l_0_colored_diff is missing else l_0_colored_diff))):
                pass
                yield escape((undefined(name='colored_diff') if l_0_colored_diff is missing else l_0_colored_diff))
            else:
                pass
                yield escape(environment.getattr((undefined(name='document') if l_0_document is missing else l_0_document), 'reserved_uid'))
        else:
            pass
            yield escape(environment.getattr((undefined(name='document') if l_0_document is missing else l_0_document), 'reserved_uid'))
        yield '</div>\n\n'
    yield '\n\n'
    l_0_title_modified = ((not t_1((undefined(name='document_change') if l_0_document_change is missing else l_0_document_change))) and environment.getattr((undefined(name='document_change') if l_0_document_change is missing else l_0_document_change), 'title_modified'))
    context.vars['title_modified'] = l_0_title_modified
    context.exported_vars.add('title_modified')
    yield '\n<div\n  class="diff_node_field"\n  '
    if (undefined(name='title_modified') if l_0_title_modified is missing else l_0_title_modified):
        pass
        yield '\n  modified="'
        yield escape((undefined(name='side') if l_0_side is missing else l_0_side))
        yield '"\n  '
    yield '\n>'
    l_1_badge_text = 'title'
    pass
    template = environment.get_template('components/badge/index.jinja', 'features/diff_and_changelog/fields/document_fields.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'badge_text': l_1_badge_text, 'colored_diff': l_0_colored_diff, 'document_change': l_0_document_change, 'node': l_0_node, 'title_modified': l_0_title_modified, 'uid_modified': l_0_uid_modified}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_badge_text = missing
    yield '<div\n    class="sdoc_pre_content"\n  >'
    if (undefined(name='title_modified') if l_0_title_modified is missing else l_0_title_modified):
        pass
        l_0_colored_diff = context.call(environment.getattr((undefined(name='document_change') if l_0_document_change is missing else l_0_document_change), 'get_colored_title_diff'), (undefined(name='side') if l_0_side is missing else l_0_side))
        context.vars['colored_diff'] = l_0_colored_diff
        context.exported_vars.add('colored_diff')
        if (not t_1((undefined(name='colored_diff') if l_0_colored_diff is missing else l_0_colored_diff))):
            pass
            yield escape((undefined(name='colored_diff') if l_0_colored_diff is missing else l_0_colored_diff))
        else:
            pass
            yield escape(environment.getattr((undefined(name='document') if l_0_document is missing else l_0_document), 'title'))
    else:
        pass
        yield escape(environment.getattr((undefined(name='document') if l_0_document is missing else l_0_document), 'title'))
    yield '</div>\n</div>\n\n</div>'

blocks = {}
debug_info = '1=23&2=27&7=31&12=36&14=44&18=47&19=50&22=54&23=57&27=62&30=69&31=71&33=74&34=76&36=79&39=82&46=85&49=89&50=92&54=97&60=105&61=107&63=110&64=112&66=115&69=118'