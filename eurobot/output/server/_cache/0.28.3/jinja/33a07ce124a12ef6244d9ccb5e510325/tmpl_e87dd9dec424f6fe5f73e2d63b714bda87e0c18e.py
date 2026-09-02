from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'base.jinja.html'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_view_object = resolve('view_object')
    pass
    yield '<!DOCTYPE html>\n<html lang="en">\n<head>\n  '
    yield from context.blocks['head'][0](context)
    yield '\n</head>\n\n<body data-viewtype="'
    yield from context.blocks['viewtype'][0](context)
    yield '" data-turbo="false">\n\n<div class="mars">\n  '
    if environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_running_on_server'):
        pass
        yield '\n  '
        template = environment.get_template('websocket.jinja.html', 'base.jinja.html')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '\n  '
    yield '\n</div>\n\n  <div class="layout" id="layout">\n\n    <nav class="layout_nav">\n      '
    yield from context.blocks['layout_nav'][0](context)
    yield '\n    </nav>\n\n    <aside class="layout_tree">\n      '
    yield from context.blocks['tree_content'][0](context)
    yield '\n    </aside>'
    l_1_toc_position = 'right'
    pass
    yield '<aside\n        data-position="'
    yield escape(l_1_toc_position)
    yield '"\n        class="layout_toc"\n      >\n        '
    yield from context.blocks['toc_content'][0](context.derived({'toc_position': l_1_toc_position}))
    yield '\n      </aside>'
    l_1_toc_position = missing
    yield '<header class="layout_header">\n      '
    yield from context.blocks['header_content'][0](context)
    yield '\n    </header>\n\n    <main class="layout_main">\n      '
    yield from context.blocks['main_content'][0](context)
    yield '\n    </main>\n\n    <footer class="layout_footer">\n      <div class="footer">\n        Built with\n        <a\n          class="strictdoc__link"\n          href="https://github.com/strictdoc-project/strictdoc"\n          target="_blank"\n        >'
    template = environment.get_template('icons/ico16_logo_s_100.svg', 'base.jinja.html')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    yield 'StrictDoc</a>\n        <a\n          class="strictdoc__version"\n          href="https://github.com/strictdoc-project/strictdoc/releases/tag/'
    yield escape(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'strictdoc_version'))
    yield '"\n          target="_blank"\n        >\n          <svg height="16" viewBox="0 0 16 16" version="1.1" width="16" >\n            <path fill-rule="evenodd" d="M2.5 7.775V2.75a.25.25 0 01.25-.25h5.025a.25.25 0 01.177.073l6.25 6.25a.25.25 0 010 .354l-5.025 5.025a.25.25 0 01-.354 0l-6.25-6.25a.25.25 0 01-.073-.177zm-1.5 0V2.75C1 1.784 1.784 1 2.75 1h5.025c.464 0 .91.184 1.238.513l6.25 6.25a1.75 1.75 0 010 2.474l-5.026 5.026a1.75 1.75 0 01-2.474 0l-6.25-6.25A1.75 1.75 0 011 7.775zM6 5a1 1 0 100 2 1 1 0 000-2z"/>\n          </svg>\n          '
    yield escape(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'strictdoc_version'))
    yield '\n        </a>\n      </div>\n    </footer>\n\n    <aside class="layout_aside">\n      '
    yield from context.blocks['aside_content'][0](context)
    yield '\n    </aside>\n\n  </div>\n  \n  <div id="modal"></div>\n  <div id="confirm"></div>\n  '
    yield from context.blocks['scripts'][0](context)
    yield '\n\n</body>\n</html>'

def block_head(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_view_object = resolve('view_object')
    pass
    yield '\n  <meta charset="UTF-8"/>\n  <meta name="keywords" content="strictdoc, documentation, documentation-tool, requirements-management, requirements, documentation-generator, requirement-specifications, requirements-engineering, technical-documentation, requirements-specification"/>\n  <meta name="description" content="strictdoc. Software for technical documentation and requirements management."/>\n  '
    if environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'is_running_on_server'):
        pass
        yield '<meta name="strictdoc-export-type" content="webserver">\n  '
    else:
        pass
        yield '<meta name="strictdoc-export-type" content="static">'
    yield '\n  <meta name="strictdoc-document-level" content="'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'get_document_level'), _block_vars=_block_vars))
    yield '">\n\n  <link rel="shortcut icon" href="'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_static_url'), context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'get_favicon_filename'), _block_vars=_block_vars), _block_vars=_block_vars))
    yield '" type="'
    yield escape(context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'get_favicon_mime_type'), _block_vars=_block_vars))
    yield '" />\n\n  '
    yield from context.blocks['head_css'][0](context)
    yield '\n\n  '
    yield from context.blocks['head_scripts'][0](context)
    yield '\n\n  <title>'
    yield from context.blocks['title'][0](context)
    yield '</title>\n\n  '

def block_head_css(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    l_0_view_object = resolve('view_object')
    pass
    yield '\n  <link rel="stylesheet" href="'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_static_url'), 'base.css', _block_vars=_block_vars))
    yield '"/>\n  <link rel="stylesheet" href="'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_static_url'), 'layout.css', _block_vars=_block_vars))
    yield '"/>\n  <link rel="stylesheet" href="'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_static_url'), 'content.css', _block_vars=_block_vars))
    yield '"/>\n  <link rel="stylesheet" href="'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_static_url'), 'node.css', _block_vars=_block_vars))
    yield '"/>\n  <link rel="stylesheet" href="'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_static_url'), 'node_content.css', _block_vars=_block_vars))
    yield '"/>\n  <link rel="stylesheet" href="'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_static_url'), 'element.css', _block_vars=_block_vars))
    yield '"/>\n  <link rel="stylesheet" href="'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_static_url'), 'form.css', _block_vars=_block_vars))
    yield '"/>\n  <link rel="stylesheet" href="'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_static_url'), 'requirement__temporary.css', _block_vars=_block_vars))
    yield '"/>\n  <link rel="stylesheet" href="'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_static_url'), 'autogen.css', _block_vars=_block_vars))
    yield '"/>\n  <link rel="stylesheet" href="'
    yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_static_url'), 'pygments.css', _block_vars=_block_vars))
    yield '"/>\n  '
    if environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'custom_css_path'):
        pass
        yield '\n  <link rel="stylesheet" href="'
        yield escape(context.call(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'render_static_url'), context.call(environment.getattr(environment.getattr((undefined(name='view_object') if l_0_view_object is missing else l_0_view_object), 'project_config'), 'get_custom_css_filename'), _block_vars=_block_vars), _block_vars=_block_vars))
        yield '"/>\n  '
    yield '\n  '

def block_head_scripts(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\n  \n  '

def block_title(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass

def block_viewtype(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass

def block_layout_nav(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass
    yield '\n      \n      '

def block_tree_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass

def block_toc_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass

def block_header_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass

def block_main_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass

def block_aside_content(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass

def block_scripts(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    _block_vars = {}
    pass

blocks = {'head': block_head, 'head_css': block_head_css, 'head_scripts': block_head_scripts, 'title': block_title, 'viewtype': block_viewtype, 'layout_nav': block_layout_nav, 'tree_content': block_tree_content, 'toc_content': block_toc_content, 'header_content': block_header_content, 'main_content': block_main_content, 'aside_content': block_aside_content, 'scripts': block_scripts}
debug_info = '4=13&42=15&45=17&46=20&53=28&59=30&64=35&67=37&72=41&76=43&86=45&89=52&95=54&101=56&108=58&4=61&8=71&13=78&15=80&17=84&33=86&37=88&17=91&18=101&19=103&20=105&21=107&22=109&23=111&24=113&25=115&26=117&27=119&28=121&29=124&33=128&37=138&42=147&53=156&59=166&67=175&72=184&76=193&101=202&108=211'