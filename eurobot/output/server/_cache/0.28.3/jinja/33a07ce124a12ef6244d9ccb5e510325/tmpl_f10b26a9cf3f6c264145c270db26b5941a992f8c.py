from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = '_shared/nav.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    l_0_project_statistics_feature = missing
    try:
        t_1 = environment.tests['none']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'none' found.")
    pass
    yield '<div class="nav">\n\n\n\n  <a\n    data-link="index"\n    class="nav_button"\n    href="'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_url'), 'index.html'))
    yield '"\n    title="Project index"\n    data-testid="project-tree-link-project-index"\n  >\n    '
    template = environment.get_template('icons/ico16_index.svg', '_shared/nav.jinja.html')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'project_statistics_feature': l_0_project_statistics_feature}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n  </a>'
    l_0_project_statistics_feature = context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'get_feature'), 'PROJECT_STATISTICS_SCREEN')
    context.vars['project_statistics_feature'] = l_0_project_statistics_feature
    context.exported_vars.add('project_statistics_feature')
    if (not t_1((undefined(name='project_statistics_feature') if l_0_project_statistics_feature is missing else l_0_project_statistics_feature))):
        pass
        yield '<a\n    data-link="project_information"\n    class="nav_button"\n    href="'
        yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_url'), 'project_statistics.html'))
        yield '"\n    title="Project statistics"\n    data-testid="project-tree-link-project-statistics"\n  >\n    '
        template = environment.get_or_select_template(context.call(environment.getattr((undefined(name='project_statistics_feature') if l_0_project_statistics_feature is missing else l_0_project_statistics_feature), 'screen_icon')), '_shared/nav.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'project_statistics_feature': l_0_project_statistics_feature}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n  </a>'
    if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_activated_requirements_coverage')):
        pass
        yield '<a\n    data-link="traceability-matrix"\n    class="nav_button"\n    href="'
        yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_url'), 'traceability_matrix.html'))
        yield '"\n    title="Traceability matrix"\n    data-testid="project-tree-link-requirements-coverage"\n  >\n    '
        template = environment.get_template('icons/ico16_requirement.svg', '_shared/nav.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'project_statistics_feature': l_0_project_statistics_feature}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n  </a>'
    if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_activated_requirements_to_source_traceability')):
        pass
        yield '<a\n    data-link="source_coverage"\n    class="nav_button"\n    href="'
        yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_url'), 'source_coverage.html'))
        yield '"\n    title="Source coverage"\n    data-testid="project-tree-link-source-coverage"\n  >\n    '
        template = environment.get_template('icons/ico16_source.svg', '_shared/nav.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'project_statistics_feature': l_0_project_statistics_feature}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n  </a>'
    if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_activated_search')):
        pass
        yield '<a\n    data-link="search"\n    class="nav_button"\n    href="'
        yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_url'), 'search'))
        yield '"\n    title="Search"\n    data-testid="project-tree-link-search"\n  >\n    '
        template = environment.get_template('icons/ico16_search.svg', '_shared/nav.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'project_statistics_feature': l_0_project_statistics_feature}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n  </a>'
    if ((environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_running_on_server') or environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'diff_page')) and context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_activated_diff'))):
        pass
        yield '<a\n    data-link="diff"\n    class="nav_button"'
        if environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_running_on_server'):
            pass
            yield 'href="'
            yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_url'), 'diff'))
            yield '"'
        else:
            pass
            yield 'href="'
            yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_url'), 'diff.html'))
            yield '"'
        yield 'title="Diff"\n    data-testid="project-tree-link-diff"\n  >\n    '
        template = environment.get_template('icons/ico16_diff.svg', '_shared/nav.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'project_statistics_feature': l_0_project_statistics_feature}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n  </a>'
    if context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_activated_tree_map')):
        pass
        yield '<a\n    data-link="tree_map"\n    class="nav_button"\n    href="'
        yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_url'), 'tree_map.html'))
        yield '"\n    title="Tree map"\n    data-testid="project-tree-link-tree-map"\n  >\n    M\n  </a>'
    yield '</div>'

blocks = {}
debug_info = '8=20&12=22&15=29&16=32&20=35&24=37&28=44&32=47&36=49&40=56&44=59&48=61&52=68&56=71&60=73&64=80&68=83&69=86&71=91&76=94&80=101&84=104'