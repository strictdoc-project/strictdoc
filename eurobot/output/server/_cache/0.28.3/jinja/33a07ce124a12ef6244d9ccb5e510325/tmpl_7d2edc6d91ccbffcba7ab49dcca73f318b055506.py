from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'features/source_file_view/index.jinja'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    parent_template = None
    l_0_template_type = missing
    pass
    l_0_template_type = 'Source file coverage'
    context.vars['template_type'] = l_0_template_type
    context.exported_vars.add('template_type')
    if parent_template is None:
        yield '\n\n'
    parent_template = environment.get_template('base.jinja.html', 'features/source_file_view/index.jinja')
    for name, parent_block in parent_template.blocks.items():
        context.blocks.setdefault(name, []).append(parent_block)
    yield from parent_template.root_render_func(context)

def block_head_css(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_super = context.super('head_css', block_head_css)
    _block_vars = {}
    l_0_view_object = resolve('view_object')
    pass
    yield '\n  '
    yield escape(context.call(l_0_super, _block_vars=_block_vars))
    yield '\n  <link rel="stylesheet" href="'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_static_url'), 'source_file_screen.css', _block_vars=_block_vars))
    yield '" />\n  <link rel="stylesheet" href="'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_static_url'), 'requirement-tree.css', _block_vars=_block_vars))
    yield '"/>\n'

def block_head_scripts(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_super = context.super('head_scripts', block_head_scripts)
    _block_vars = {}
    l_0_view_object = resolve('view_object')
    pass
    yield '\n  <script src="'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_static_url'), 'source_file_screen.js', _block_vars=_block_vars))
    yield '"></script>\n  '
    yield escape(context.call(l_0_super, _block_vars=_block_vars))
    yield '\n'

def block_title(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_view_object = resolve('view_object')
    l_0_template_type = resolve('template_type')
    pass
    yield '\n  '
    yield escape(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'source_file'), 'in_doctree_source_file_rel_path_posix'))
    yield ' - '
    yield escape((undefined(name='template_type') if l_0_template_type is missing else l_0_template_type))
    yield '\n'

def block_viewtype(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield 'source-file'

def block_head(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_super = context.super('head', block_head)
    _block_vars = {}
    l_0_view_object = resolve('view_object')
    pass
    yield '\n  '
    yield escape(context.call(l_0_super, _block_vars=_block_vars))
    yield '\n\n  <style>\n    '
    yield escape(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'pygments_styles'))
    yield '\n  </style>\n'

def block_layout_nav(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\n  '
    template = environment.get_template('_shared/nav.jinja.html', 'features/source_file_view/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n'

def block_header_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_template_type = resolve('template_type')
    pass
    l_1_header__items = ['features/source_file_view/header__source_file_name.jinja']
    l_1_header__pagetype = (undefined(name='template_type') if l_0_template_type is missing else l_0_template_type)
    l_1_header__last = 'features/source_file_view/header__actions.jinja'
    pass
    template = environment.get_template('components/header/index.jinja', 'features/source_file_view/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'header__items': l_1_header__items, 'header__last': l_1_header__last, 'header__pagetype': l_1_header__pagetype}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    l_1_header__items = l_1_header__pagetype = l_1_header__last = missing

def block_tree_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\n  '
    template = environment.get_template('features/source_file_view/aside.jinja', 'features/source_file_view/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n'

def block_main_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\n  '
    template = environment.get_template('features/source_file_view/main.jinja', 'features/source_file_view/index.jinja')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield '\n'

blocks = {'head_css': block_head_css, 'head_scripts': block_head_scripts, 'title': block_title, 'viewtype': block_viewtype, 'head': block_head, 'layout_nav': block_layout_nav, 'header_content': block_header_content, 'tree_content': block_tree_content, 'main_content': block_main_content}
debug_info = '1=13&3=18&5=23&6=34&7=36&8=38&10=41&11=52&12=54&15=57&16=68&19=73&21=83&22=94&25=96&29=99&30=108&33=116&39=129&43=137&44=146&47=154&48=163'