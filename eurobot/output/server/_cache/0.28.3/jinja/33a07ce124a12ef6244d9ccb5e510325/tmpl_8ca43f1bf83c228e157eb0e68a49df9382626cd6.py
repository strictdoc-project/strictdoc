from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/traceability_matrix/project_tree_flat_anchor_list.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    pass
    yield '<div class="tree">'
    l_1_loop = missing
    for l_1_document, l_1_loop in LoopContext(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'iterate_documents')), undefined):
        _loop_vars = {}
        pass
        yield '<a\n      href="#'
        yield escape(environment.getattr(l_1_loop, 'index'))
        yield '"\n      class="tree_item"\n      data-testid="tree-document-anchor"\n    >\n      '
        template = environment.get_template('icons/ico16_document.svg', 'features/traceability_matrix/project_tree_flat_anchor_list.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'document': l_1_document, 'loop': l_1_loop}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n      <div\n        class="document_title"\n        title="'
        yield escape(environment.getattr(l_1_document, 'title'))
        yield '"\n        data-file_name=""\n      >'
        yield escape(environment.getattr(l_1_document, 'title'))
        yield '</div>\n    </a>'
    l_1_loop = l_1_document = missing
    yield '</div>'

blocks = {}
debug_info = '2=14&4=18&8=20&11=27&13=29'