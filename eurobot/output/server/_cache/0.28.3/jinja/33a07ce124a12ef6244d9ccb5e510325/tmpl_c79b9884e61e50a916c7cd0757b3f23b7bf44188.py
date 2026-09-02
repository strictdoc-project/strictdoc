from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/traceability_matrix/resizable_bar_with_project_tree.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    pass
    l_1_resizable_bar_content = 'features/traceability_matrix/project_tree_flat_anchor_list.jinja'
    l_1_resizable_bar_name = 'tree'
    pass
    template = environment.get_template('components/resizable_bar/index.jinja', 'features/traceability_matrix/resizable_bar_with_project_tree.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'resizable_bar_content': l_1_resizable_bar_content, 'resizable_bar_name': l_1_resizable_bar_name}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_resizable_bar_content = l_1_resizable_bar_name = missing

blocks = {}
debug_info = '5=14'