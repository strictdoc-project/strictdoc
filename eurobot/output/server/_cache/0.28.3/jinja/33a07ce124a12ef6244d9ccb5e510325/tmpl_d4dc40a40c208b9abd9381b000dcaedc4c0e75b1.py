from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/project_index/main.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_external_ = resolve('external_')
    l_0_internal_ = resolve('internal_')
    try:
        t_1 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    try:
        t_2 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    yield '<div class="main">\n  <div class="dashboard">\n    <div class="dashboard-main">\n      '
    template = environment.get_template('features/project_index/frame_project_tree.jinja.html', 'features/project_index/main.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'external_': l_0_external_, 'internal_': l_0_internal_}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n    </div>\n    <div class="dashboard-aside">\n      '
    if context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'should_display_fragments_toggle')):
        pass
        yield '\n      <div class="dashboard-block" id="project_tree_controls"></div>\n      '
    yield '\n\n      <div class="dashboard-block">\n        \n        \n        <div class="dashboard-block-title">\n          Project tree configuration\n        </div>\n\n        '
    if t_1(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'input_paths')):
        pass
        yield '\n          <b>Input paths:</b>\n          '
        for l_1_path_ in environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'input_paths'):
            l_1_external_ = l_0_external_
            l_1_internal_ = l_0_internal_
            _loop_vars = {}
            pass
            yield '\n          '
            (l_1_external_, l_1_internal_) = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'split_path_for_display'), l_1_path_, _loop_vars=_loop_vars)
            _loop_vars.update({'external_': l_1_external_, 'internal_': l_1_internal_})
            yield '\n          <code class="dashboard-path" data-testid="dashboard-input-path">'
            if (undefined(name='external_') if l_1_external_ is missing else l_1_external_):
                pass
                yield '<span class="dashboard-path-external" data-testid="dashboard-input-path-external" tabindex="0" title="Click to reveal">…</span><span class="dashboard-path-external-full">'
                yield escape((undefined(name='external_') if l_1_external_ is missing else l_1_external_))
                yield '</span>'
            yield '<span class="dashboard-path-internal">'
            yield escape((undefined(name='internal_') if l_1_internal_ is missing else l_1_internal_))
            yield '</span>\n          </code><br/>\n          '
        l_1_path_ = l_1_external_ = l_1_internal_ = missing
        yield '\n        '
    yield '\n\n        '
    if (t_1(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'include_doc_paths')) or t_1(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'exclude_doc_paths'))):
        pass
        yield '\n          <p>Document paths:</p>\n          <ul>\n            '
        for l_1_path_ in environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'include_doc_paths'):
            _loop_vars = {}
            pass
            yield '\n            <li style="list-style-type: \'✔️    \'">'
            yield escape(l_1_path_)
            yield '</li>\n            '
        l_1_path_ = missing
        yield '\n            '
        for l_1_path_ in environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'exclude_doc_paths'):
            _loop_vars = {}
            pass
            yield '\n            <li style="list-style-type: \'⛔    \'">'
            yield escape(l_1_path_)
            yield '</li>\n            '
        l_1_path_ = missing
        yield '\n          </ul>\n        '
    yield '\n\n        '
    if (not t_2(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'source_root_path'))):
        pass
        yield '\n          '
        (l_0_external_, l_0_internal_) = context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'split_path_for_display'), environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'source_root_path'))
        context.vars.update({'external_': l_0_external_, 'internal_': l_0_internal_})
        context.exported_vars.update(('external_', 'internal_'))
        yield '\n          <b>Source root path:</b>\n            <code class="dashboard-path" data-testid="dashboard-source-root-path">'
        if (undefined(name='external_') if l_0_external_ is missing else l_0_external_):
            pass
            yield '<span class="dashboard-path-external" data-testid="dashboard-source-root-path-external" tabindex="0" title="Click to reveal">…</span><span class="dashboard-path-external-full">'
            yield escape((undefined(name='external_') if l_0_external_ is missing else l_0_external_))
            yield '</span>'
        yield '<span class="dashboard-path-internal">'
        yield escape((undefined(name='internal_') if l_0_internal_ is missing else l_0_internal_))
        yield '</span>\n            </code>\n        '
    yield '\n\n        '
    if (t_1(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'include_source_paths')) or t_1(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'exclude_source_paths'))):
        pass
        yield '\n          <p>Source paths:</p>\n          <ul>\n            '
        for l_1_path_ in environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'include_source_paths'):
            _loop_vars = {}
            pass
            yield '\n            <li style="list-style-type: \'✔️    \'">'
            yield escape(l_1_path_)
            yield '</li>\n            '
        l_1_path_ = missing
        yield '\n            '
        for l_1_path_ in environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'exclude_source_paths'):
            _loop_vars = {}
            pass
            yield '\n            <li style="list-style-type: \'⛔    \'">'
            yield escape(l_1_path_)
            yield '</li>\n            '
        l_1_path_ = missing
        yield '\n          </ul>\n        '
    yield '\n\n      </div>\n    </div>\n  </div>\n</div>'

blocks = {}
debug_info = '4=27&7=34&18=38&20=41&21=47&23=50&24=53&26=56&31=61&34=64&35=68&37=72&38=76&43=81&44=84&47=88&48=91&50=94&54=97&57=100&58=104&60=108&61=112'