from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/traceability_matrix/requirement.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_requirement = resolve('requirement')
    l_0_relation_type = resolve('relation_type')
    try:
        t_1 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    try:
        t_2 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    def macro():
        t_3 = []
        pass
        return concat(t_3)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, (t_1((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement)) and (not t_2((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement)))), None, caller=caller)
    yield '\n\n<sdoc-node\n  node-style="card"\n  node-role="requirement"\n  js-requirements-coverage'
    if environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_status'):
        pass
        yield "\n  data-status='"
        yield escape(context.call(environment.getattr(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_status'), 'lower')))
        yield "'"
    if environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_uid'):
        pass
        yield "\n  data-uid='"
        yield escape(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_uid'))
        yield "'"
    yield '\n>\n  <div\n    class="traceability_matrix__requirement"\n    '
    if t_1((undefined(name='relation_type') if l_0_relation_type is missing else l_0_relation_type)):
        pass
        yield '\n    with_relation="'
        yield escape((undefined(name='relation_type') if l_0_relation_type is missing else l_0_relation_type))
        yield '"\n    '
    yield '\n    data-level="'
    yield escape(environment.getattr(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'context'), 'title_number_string'))
    yield '"\n  >\n    <small><b '
    if t_2(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_uid')):
        pass
        yield 'style="color:red"'
    yield '>'
    yield escape((environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_uid') if environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_uid') else '[No UID]'))
    yield '</b></small>\n    <br/>'
    if environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_title'):
        pass
        if environment.getattr(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'context'), 'title_number_string'):
            pass
            yield '\n        '
            yield escape(environment.getattr(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'context'), 'title_number_string'))
            yield '.&nbsp;'
        yield escape(environment.getattr((undefined(name='requirement') if l_0_requirement is missing else l_0_requirement), 'reserved_title'))
    yield '\n  </div>\n</sdoc-node>'

blocks = {}
debug_info = '1=25&7=32&8=35&10=37&11=40&16=43&17=46&19=49&21=51&23=57&24=59&25=62&27=64'