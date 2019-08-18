from markdown import markdown
import makeCourse.markdownRenderer.codemirror

def render_markdown(content):
    return markdown(content,
            extensions=[
                'pymdownx.highlight',
                'pymdownx.arithmatex',
                'pymdownx.extra',
                'pymdownx.superfences'
            ],
            extension_configs={
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
                    }]
                }
            })
