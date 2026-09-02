from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/diff_and_changelog/node/requirement.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_requirement = resolve('requirement')
    l_0_side = resolve('side')
    l_0_tab = resolve('tab')
    l_0_requirement_token = resolve('requirement_token')
    l_0_requirement_change = missing
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
    l_0_requirement_change = context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'change_stats'), 'find_change'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement))
    context.vars['requirement_change'] = l_0_requirement_change
    context.exported_vars.add('requirement_change')
    yield '\n\n<details\n  class="diff_node"\n  '
    if (not t_2((undefined(name='requirement_change') if l_0_requirement_change is missing else l_0_requirement_change))):
        pass
        yield '\n    modified="'
        yield escape((undefined(name='side') if l_0_side is missing else l_0_side))
        yield '"\n  '
    yield '\n>\n  <summary>\n    '
    l_1_badge_text = context.call(environment.getattr(environment.getitem(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'node_type'), 0), 'upper'))
    pass
    template = environment.get_template('components/badge/index.jinja', 'features/diff_and_changelog/node/requirement.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'badge_text': l_1_badge_text, 'requirement_change': l_0_requirement_change, 'requirement_token': l_0_requirement_token}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_badge_text = missing
    yield '<span>\n      '
    yield escape((environment.getattr(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'context'), 'title_number_string') if environment.getattr(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'context'), 'title_number_string') else (Markup('&nbsp;') * ((environment.getattr(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'context'), 'ng_level') * 2) - 1))))
    yield '\n    </span>'
    if (not t_2(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_title'))):
        pass
        yield '<span>\n        '
        yield escape(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_title'))
        yield '\n      </span>'
    if ((undefined(name='tab') if l_0_tab is missing else l_0_tab) == 'diff'):
        pass
        if (not t_2((undefined(name='requirement_change') if l_0_requirement_change is missing else l_0_requirement_change))):
            pass
            l_0_requirement_token = environment.getattr((undefined(name='requirement_change') if l_0_requirement_change is missing else l_0_requirement_change), 'requirement_token')
            context.vars['requirement_token'] = l_0_requirement_token
            context.exported_vars.add('requirement_token')
            if (not t_2((undefined(name='requirement_token') if l_0_requirement_token is missing else l_0_requirement_token))):
                pass
                l_1_uid = (undefined(name='requirement_token') if l_0_requirement_token is missing else l_0_requirement_token)
                pass
                template = environment.get_template('features/diff_and_changelog/sync/button.jinja', 'features/diff_and_changelog/node/requirement.jinja')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'uid': l_1_uid, 'requirement_change': l_0_requirement_change, 'requirement_token': l_0_requirement_token}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
                l_1_uid = missing
    yield '</summary>\n\n  '
    template = environment.get_template('features/diff_and_changelog/fields/requirement_fields.jinja', 'features/diff_and_changelog/node/requirement.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'requirement_change': l_0_requirement_change, 'requirement_token': l_0_requirement_token}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n\n</details>'

blocks = {}
debug_info = '1=29&5=33&6=36&16=41&19=49&21=51&23=54&26=56&27=58&28=60&29=63&31=67&38=75'