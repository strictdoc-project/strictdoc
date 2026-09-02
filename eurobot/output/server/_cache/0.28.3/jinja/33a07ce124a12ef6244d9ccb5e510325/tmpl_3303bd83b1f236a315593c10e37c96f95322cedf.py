from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = '_shared/requirement_tree_right.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_requirement = resolve('requirement')
    pass
    yield '\n'
    if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'has_children_requirements'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement)):
        pass
        yield '\n\n<ul class="requirement-tree requirement-tree_right">'
        for l_1_requirement in context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'get_children_requirements'), (undefined(name='requirement') if l_0_requirement is missing else l_0_requirement)):
            l_1_requirement_partial = resolve('requirement_partial')
            _loop_vars = {}
            pass
            yield '<li class="requirement-tree_branch">\n    <div class="requirement-tree_node">\n      '
            template = environment.get_or_select_template((undefined(name='requirement_partial') if l_1_requirement_partial is missing else l_1_requirement_partial), '_shared/requirement_tree_right.jinja.html')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'requirement': l_1_requirement}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            yield '\n    </div>'
            if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document_type'), 'is_deeptrace'), _loop_vars=_loop_vars):
                pass
                template = environment.get_template('_shared/requirement_tree_right.jinja.html', '_shared/requirement_tree_right.jinja.html')
                gen = template.root_render_func(template.new_context(context.get_all(), True, {'requirement': l_1_requirement}))
                try:
                    for event in gen:
                        yield event
                finally: gen.close()
            yield '\n\n  </li>'
        l_1_requirement = l_1_requirement_partial = missing
        yield '</ul>'

blocks = {}
debug_info = '4=14&7=17&11=22&14=29&15=31'