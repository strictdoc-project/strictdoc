from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/_shared/project_tree_child_documents.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_document = resolve('document')
    pass
    if context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'should_display_included_documents_for_document'), (undefined(name='document') if l_0_document is missing else l_0_document)):
        pass
        yield '\n<ul class="tree_fragments">\n'
        for l_1_child_document_ in environment.getattr((undefined(name='document') if l_0_document is missing else l_0_document), 'included_documents'):
            _loop_vars = {}
            pass
            yield '\n  <li>\n    <a\n      class="tree_item"\n      '
            if (environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document') == l_1_child_document_):
                pass
                yield '\n      active="true"\n      '
            yield '\n      data-testid="tree-document-fragment-link"\n      href="'
            yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_current_view_document_link'), l_1_child_document_, _loop_vars=_loop_vars))
            yield '"\n    >'
            template = environment.get_template('icons/ico16_fragment.svg', 'screens/document/_shared/project_tree_child_documents.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'child_document_': l_1_child_document_}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            yield '<div\n        class="document_title"\n        title="'
            yield escape(environment.getattr(l_1_child_document_, 'title'))
            yield '"\n        data-file_name="'
            yield escape(environment.getattr(environment.getattr(l_1_child_document_, 'meta'), 'document_filename'))
            yield '"\n      >'
            yield escape(environment.getattr(l_1_child_document_, 'title'))
            yield '</div>\n    </a>\n\n    '
            l_2_document = l_1_child_document_
            pass
            yield '\n    '
            template = environment.get_template('screens/document/_shared/project_tree_child_documents.jinja', 'screens/document/_shared/project_tree_child_documents.jinja')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'document': l_2_document, 'child_document_': l_1_child_document_}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
            yield '\n    '
            l_2_document = missing
            yield '\n  </li>\n'
        l_1_child_document_ = missing
        yield '\n</ul>\n'

blocks = {}
debug_info = '1=13&3=16&7=20&11=24&13=26&16=33&17=35&18=37&22=42'