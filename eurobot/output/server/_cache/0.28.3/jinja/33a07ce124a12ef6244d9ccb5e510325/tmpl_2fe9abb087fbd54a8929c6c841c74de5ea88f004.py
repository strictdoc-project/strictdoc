from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'components/form/search.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    try:
        t_1 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    try:
        t_2 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    try:
        t_3 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    def macro():
        t_4 = []
        pass
        return concat(t_4)
    caller = Macro(environment, macro, None, (), False, False, False, context.eval_ctx.autoescape)
    yield context.call(environment.extensions['strictdoc.export.html.jinja.assert_extension.AssertExtension']._assert, t_2(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'error')), None, caller=caller)
    yield '\n\n<sdoc-form search\n '
    if (t_3(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'error')) and (t_1(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'search_results')) > 0)):
        pass
        yield 'success'
    yield '\n>\n\n  <form\n    action="/search"\n    method="GET"\n  >\n      <input\n        type="text"\n        value="'
    yield escape(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'search_value'))
    yield '"\n        placeholder="Enter search query here"\n        id="q"\n        name="q"\n      />\n      '
    template = environment.get_template('components/button/search.jinja', 'components/form/search.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n  </form>'
    if (t_1(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'search_value')) > 0):
        pass
        if t_3(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'error')):
            pass
            if (t_1(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'search_results')) == 0):
                pass
                yield '<div class="sdoc-form-success">Nothing matching the query was found.</div>'
            elif (t_1(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'search_results')) > 0):
                pass
                yield '<div class="sdoc-form-success">Found <b>'
                yield escape(t_1(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'search_results')))
                yield '</b> results.</div>'
        else:
            pass
            yield '<div class="sdoc-form-error">'
            yield escape(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'error'))
            yield '</div>'
        yield '<a class="sdoc-form-reset" href="'
        yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_url'), 'search'))
        yield '">Clear query</a>'
    yield '</sdoc-form>'

blocks = {}
debug_info = '1=30&4=37&13=41&18=43&21=50&22=52&23=54&25=57&26=60&29=65&31=68'