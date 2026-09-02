from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = '_shared/tags.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    pass
    if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'has_tags'), environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document')):
        pass
        yield '\n\n<div class="tags">'
        for (l_1_tag_name_, l_1_tag_count_) in context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'traceability_index'), 'get_counted_tags'), environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'document')):
            _loop_vars = {}
            pass
            yield '\n  <span class="tag">\n    '
            yield escape(l_1_tag_name_)
            yield '<span class="tag_badge">'
            yield escape(l_1_tag_count_)
            yield '</span>\n  </span>\n'
        l_1_tag_name_ = l_1_tag_count_ = missing
        yield '</div>'

blocks = {}
debug_info = '1=12&11=15&13=19'