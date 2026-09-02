from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/form/field_action_button/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_action_button_context = resolve('action_button_context')
    try:
        t_1 = environment.filters['default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'default' found.")
    try:
        t_2 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    try:
        t_3 = environment.tests['sameas']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No test named 'sameas' found.")
    pass
    def macro():
        t_4 = []
        pass
        return concat(t_4)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_2((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context)), None, caller=caller)
    def macro():
        t_5 = []
        pass
        return concat(t_5)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_2(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'field_actions')), None, caller=caller)
    def macro():
        t_6 = []
        pass
        return concat(t_6)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_2(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'field_name')), None, caller=caller)
    def macro():
        t_7 = []
        pass
        return concat(t_7)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_2(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'mid')), 'mid is not defined', caller=caller)
    def macro():
        t_8 = []
        pass
        return concat(t_8)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_2(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'testid_postfix')), 'testid_postfix is not defined', caller=caller)
    if (t_2(environment.getattr(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'field_actions'), 'move_up')) and t_3(environment.getattr(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'field_actions'), 'move_up'), True)):
        pass
        yield '<button\n    class="field_action"\n    mid="'
        yield escape(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'mid'))
        yield '"\n    title="Move this '
        yield escape(t_1(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'field_name'), 'FIELD', True))
        yield ' up"\n    data-action-type="move_up"\n    data-js-move-up-field-action\n    data-turbo-action="replace"\n    data-turbo="false"\n    data-testid="form-move-up-field-action-'
        yield escape(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'testid_postfix'))
        yield '"\n  >'
        template = environment.get_template('icons/ico16_move_up.svg', 'components/form/field_action_button/index.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '</button>'
    if (t_2(environment.getattr(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'field_actions'), 'move_down')) and t_3(environment.getattr(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'field_actions'), 'move_down'), True)):
        pass
        yield '<button\n    class="field_action"\n    mid="'
        yield escape(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'mid'))
        yield '"\n    title="Move this '
        yield escape(t_1(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'field_name'), 'FIELD', True))
        yield ' down"\n    data-action-type="move_down"\n    data-js-move-down-field-action\n    data-turbo-action="replace"\n    data-turbo="false"\n    data-testid="form-move-down-field-action-'
        yield escape(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'testid_postfix'))
        yield '"\n  >'
        template = environment.get_template('icons/ico16_move_down.svg', 'components/form/field_action_button/index.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '</button>'
    if (t_2(environment.getattr(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'field_actions'), 'delete')) and t_3(environment.getattr(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'field_actions'), 'delete'), True)):
        pass
        yield '<button\n    class="field_action"\n    mid="'
        yield escape(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'mid'))
        yield '"\n    title="Delete this '
        yield escape(t_1(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'field_name'), 'FIELD', True))
        yield '"\n    data-action-type="delete"\n    data-js-delete-field-action\n    data-turbo-action="replace"\n    data-turbo="false"\n    data-testid="form-delete-field-action-'
        yield escape(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'testid_postfix'))
        yield '"\n  >'
        template = environment.get_template('icons/ico16_delete.svg', 'components/form/field_action_button/index.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '</button>'
    if (t_2(environment.getattr(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'field_actions'), 'move')) and t_3(environment.getattr(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'field_actions'), 'move'), True)):
        pass
        yield '<button\n    class="field_action"\n    mid="'
        yield escape(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'mid'))
        yield '"\n    title="Move this '
        yield escape(t_1(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'field_name'), 'FIELD', True))
        yield '"\n    data-action-type="move"\n    data-js-move-field-action\n    data-turbo-action="replace"\n    data-turbo="false"\n    data-testid="form-move-field-action-'
        yield escape(environment.getattr((undefined(name='action_button_context') if l_0_action_button_context is missing else l_0_action_button_context), 'testid_postfix'))
        yield '"\n  >'
        template = environment.get_template('icons/ico16_6dots.svg', 'components/form/field_action_button/index.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '</button>'

blocks = {}
debug_info = '1=30&2=36&3=42&4=48&5=54&7=60&10=63&11=65&16=67&17=69&20=76&23=79&24=81&29=83&30=85&33=92&36=95&37=97&42=99&43=101&46=108&49=111&50=113&55=115&56=117'