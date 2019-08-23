from markdown import markdown
import makeCourse.markdownRenderer.codemirror

def render_markdown(content):
    return markdown(content,
            extensions=[
                'mdx_outline',
                'pymdownx.highlight',
                'pymdownx.arithmatex',
                'pymdownx.extra',
                'pymdownx.superfences',
            ],
            extension_configs={
                "pymdownx.arithmatex": {
                    "preview": False
                    },
                "pymdownx.superfences": {
                    "custom_fences": [{
                        'name': 'runnable',
                        'class': 'runnable',
                        'format': makeCourse.markdownRenderer.codemirror.runnable_formatter,
                        'validator': makeCourse.markdownRenderer.codemirror.runnable_validator
                    },{
                        'name': 'editable',
                        'class': 'editable',
                        'format': makeCourse.markdownRenderer.codemirror.editable_formatter,
                        'validator': makeCourse.markdownRenderer.codemirror.editable_validator
                    },{
                        'name': 'output',
                        'class': 'output',
                        'format': makeCourse.markdownRenderer.codemirror.output_formatter,
                        'validator': makeCourse.markdownRenderer.codemirror.output_validator
                    }]
                }
            })
