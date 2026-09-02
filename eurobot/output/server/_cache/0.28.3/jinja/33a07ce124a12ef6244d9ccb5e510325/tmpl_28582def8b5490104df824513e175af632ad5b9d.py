from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/project_index/project_tree_file.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_file = resolve('file')
    l_0_document = l_0_is_included = missing
    pass
    l_0_document = context.call(environment.getattr(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'document_tree'), 'get_document_by_path'), environment.getattr((undefined(name='file') if l_0_file is missing else l_0_file), 'full_path'))
    context.vars['document'] = l_0_document
    context.exported_vars.add('document')
    l_0_is_included = context.call(environment.getattr((undefined(name='document') if l_0_document is missing else l_0_document), 'document_is_included'))
    context.vars['is_included'] = l_0_is_included
    context.exported_vars.add('is_included')
    yield '\n\n<a\n  class="project_tree-file"\n  data-turbo="false"\n  href="'
    yield escape(context.call(environment.getattr(environment.getattr((undefined(name='document') if l_0_document is missing else l_0_document), 'meta'), 'get_html_doc_link')))
    yield '"\n  '
    if (undefined(name='is_included') if l_0_is_included is missing else l_0_is_included):
        pass
        yield 'included-document="is-hidden-by-default"'
    yield '\n  data-testid="tree-file-link"\n>\n\n  <div class="project_tree-file-icon">'
    if (undefined(name='is_included') if l_0_is_included is missing else l_0_is_included):
        pass
        template = environment.get_template('icons/ico16_fragment.svg', 'features/project_index/project_tree_file.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'document': l_0_document, 'is_included': l_0_is_included}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
    else:
        pass
        template = environment.get_template('icons/ico16_document.svg', 'features/project_index/project_tree_file.jinja')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'document': l_0_document, 'is_included': l_0_is_included}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
    yield '</div>\n\n  <div class="project_tree-file-details">\n    <div class="project_tree-file-title">\n      '
    yield escape(environment.getattr((undefined(name='document') if l_0_document is missing else l_0_document), 'title'))
    yield '\n    </div>\n    <div class="project_tree-file-name">\n      '
    yield escape(environment.getattr((undefined(name='file') if l_0_file is missing else l_0_file), 'file_name'))
    yield '\n    </div>'
    if (undefined(name='is_included') if l_0_is_included is missing else l_0_is_included):
        pass
        yield '<div class="project_tree-file-name">\n        <b>included by</b> '
        yield escape(environment.getattr(environment.getattr(environment.getattr(context.call(environment.getattr((undefined(name='document') if l_0_document is missing else l_0_document), 'get_including_document')), 'meta'), 'input_doc_rel_path'), 'relative_path_posix'))
        yield '\n      </div>'
    yield '</div>\n</a>'

blocks = {}
debug_info = '1=14&2=17&7=21&8=23&13=27&14=29&16=37&22=44&25=46&27=48&29=51'