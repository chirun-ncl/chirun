import {EditorView, basicSetup} from "codemirror";
import {EditorState} from "@codemirror/state";
import {python} from "@codemirror/lang-python";
import {r} from "codemirror-lang-r";

window.EditorView = EditorView;

const languages = {
    'python': python,
    'r': r
}

export default function codemirror_editor(language, options) {
    const language_plugin = languages[language];

    options = Object.assign({
        extensions: [
            basicSetup,
            language_plugin(),
            EditorView.updateListener.of(update => {
                if(!options?.onChange || update.changes.desc.empty) {
                    return;
                }
                options.onChange(update);
            })
        ]
    }, options);

    let editor = new EditorView(options);

    return editor;
}

