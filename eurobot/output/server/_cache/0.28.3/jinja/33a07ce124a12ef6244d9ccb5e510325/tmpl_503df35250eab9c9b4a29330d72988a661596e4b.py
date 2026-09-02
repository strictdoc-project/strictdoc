from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'screens/document/document/document_chunk_lazy_placeholder_static.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_chunk = resolve('chunk')
    l_0_view_object = resolve('view_object')
    try:
        t_1 = environment.filters['join']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'join' found.")
    pass
    yield '\n<turbo-frame\n  id="document-chunk-'
    yield escape(environment.getattr((undefined(name='chunk') if l_0_chunk is missing else l_0_chunk), 'index'))
    yield '"\n  class="document-chunk-placeholder"\n  data-chunk-src="'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'static_chunk_relative_path'), (undefined(name='chunk') if l_0_chunk is missing else l_0_chunk)))
    yield '"\n  data-chunk-key="'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'static_chunk_key'), (undefined(name='chunk') if l_0_chunk is missing else l_0_chunk)))
    yield '"\n  style="--document-chunk-size: '
    yield escape(environment.getattr((undefined(name='chunk') if l_0_chunk is missing else l_0_chunk), 'size'))
    yield ';"\n  data-node-mids="'
    yield escape(t_1(context.eval_ctx, environment.getattr((undefined(name='chunk') if l_0_chunk is missing else l_0_chunk), 'node_mids'), ' '))
    yield '"\n  data-anchors="'
    yield escape(t_1(context.eval_ctx, environment.getattr((undefined(name='chunk') if l_0_chunk is missing else l_0_chunk), 'anchors'), ' '))
    yield '"\n  data-testid="document-chunk-placeholder"\n></turbo-frame>'

blocks = {}
debug_info = '33=20&35=22&36=24&37=26&38=28&39=30'