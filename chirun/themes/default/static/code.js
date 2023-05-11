/** 
 * Runnable code blocks in Chirun
 * Based on the Numbas Programming Extension, Newcastle University, 2020-2022
 * https://github.com/numbas/numbas-extension-programming
 * License: Apache License 2.0
 */
import codemirror_editor from "./runnable_code.js";

var codeMirrorInstances = {};
var webR_url = 'https://cdn.jsdelivr.net/gh/georgestagg/webR@452ae1637dfdd65c9a5f462fff439022d833f8f9/dist/';

/** Objects to run code in different languages.
 * @enum {CodeRunner}
 */
var language_runners = {}

const register_language_runner = function(name, runner) {
    language_runners[name] = new runner();
}

/** An object which can run code in a certain language.
 */
class CodeRunner {
    constructor() {
        this.job_id_acc = 0;
        this.jobs = {};

        this.namespace_id_acc = 0;
        this.clear_buffers();
    }

    /** Clear the STDOUT and STDERR buffers.
     */
    clear_buffers() {
        this.buffers = {
            stdout: '',
            stderr: ''
        };
    }

    /** The contents of the STDOUT buffer after running a block of code.
     * @type {string}
     */
    get stdout() {
        return this.buffers.stdout;
    }

    /** The contents of the STDERR buffer after running a block of code.
     * @type {string}
     */
    get stderr() {
        return this.buffers.stderr;
    }

    /** Create a session using this runner.
     * @returns {CodeSession}
     */
    new_session() {
        return new CodeSession(this);
    }

    /** Create a new namespace to run code in.
     * @returns {namespace_id}
     */
    new_namespace() {
        return this.namespace_id_acc++;
    }

    /** Create a new ID for a job.
     * @returns {job}
     */
    new_job() {
        const job_id = this.job_id_acc++;
        const promise = new Promise((resolve, reject) => {
            this.jobs[job_id] = { id: job_id, resolve, reject };
        });
        const job = this.jobs[job_id];
        job.promise = promise;
        return job;
    }

    /** Get the job with the given ID, or throw an error if it doesn't exist.
     * @param {job_id} job_id
     * @returns {job}
     */
    get_job(job_id) {
        if(!this.jobs[job_id]) {
            throw(new Error(_`Unrecognised job id ${job_id}`));
        }
        return this.jobs[job_id];
    }

    /** Run some code in this runner, in the given namespace.
     * @param {string} code - The code to run.
     * @param {namespace_id} namespace_id - The ID of the namespace to run the code in.
     * @returns {job}
     */
    run_code(code, namespace_id) {
        throw(new Error(_("run_code should be implemented.")));
    }

    /** Interrupt the execution of a job.
     * @param {job_id} job_id
     */
    interrupt() {
        throw(new Error(_("This code runner can't be interrupted.")));
    }

    /** Run several blocks of code in the same session.
     *  Empty blocks of code won't run, but will return result `undefined` and success `true`.
     *
     * @param {Array.<string>} codes - Blocks of code to run.
     * @returns {Promise.<Array.<run_result>>}
     */
    async run_code_blocks(codes) {
        const session = this.new_session();
        var results = [];
        for(let code of codes) {
            if(code.trim()=='') {
              results.push({
                result: undefined,
                success: true,
                stdout: '',
                stderr: ''
              });
              continue;
            }
            try {
                const result = await session.run_code(code);
                results.push(result);
            } catch(error) {
                results.push(error);
            }
        }

        return results;
    }
}

/** An independent session to run code in.
 *  Code run in one session should not affect code run in another.
 *  @param {CodeRunner} runner
 */
class CodeSession {
    constructor(runner) {
        this.runner = runner;
        this.namespace_id = runner.new_namespace();
    }

    async run_code(code) {
        try {
            const job = await this.runner.run_code(code, this.namespace_id);
            const result = await job.promise;
            return Object.assign({success: true}, result);
        } catch(err) {
            return Object.assign({success: false}, err);
        }
    }
}

/** Load pyodide - inserts the script in the page, and returns a promise which resolves to the `pyodide` object. 
 * @returns {Promise.<pyodide>}
 */
class PyodideRunner extends CodeRunner {
    constructor() {
        super();
        var worker = this.worker = new Worker(chirun_static_url + '/pyodide_worker.js');

        worker.onmessage = (event) => {
            const job_id = event.data.job_id;
            const job = this.get_job(job_id);
            if(event.data.error) {
                job.reject(event.data);
            } else {
                job.resolve(event.data);
            }
        }
    }
    run_code(code, namespace_id) {
        const job = this.new_job();
        this.worker.postMessage({
            command: 'runPython',
            job_id: job.id,
            namespace_id: namespace_id,
            code: code
        });
        return job;
    }

    interrupt(job_id) {
        if(this.interruptBuffer) {
           this.interruptBuffer[0] = 2;
        } else {
            return super.interrupt(job_id);
        }
    }
}
register_language_runner('pyodide', PyodideRunner);

/** Load webR - inserts the script in the page, and returns a promise which resolves to the `webR` object. 
 * @returns {Promise.<webR>}
 */
class WebRRunner extends CodeRunner {
    constructor() {
        super();
    }

    new_session() {
        const session = super.new_session();
        this.run_code(`${this.namespace_name(session.namespace_id)} <- new.env()`);
        return session;
    }

    namespace_name(namespace_id) {
        return `webr_namespace${namespace_id}`;
    }

    /** Clear the STDOUT and STDERR buffers.
     */
    clear_buffers() {
        this.buffers = {
            stdout: [],
            stderr: []
        };
    }

    /** Start loading webR.
     * @returns {Promise} - Resolves to the `webR` object once it has loaded.
     */
    load_webR() {
        if(!this.webRPromise) {

            var script = document.createElement('script');
            script.setAttribute('src',webR_url + 'webR.js');
            document.head.appendChild(script);

            this.webRPromise = new Promise((resolve, reject) => {
                var checkInterval = setInterval(async () => {
                    if(window.loadWebR) {
                        clearInterval(checkInterval);
                        const webR = await loadWebR({
                            WEBR_URL: webR_url,
                            loadPackages: [],
                            stdout: (s) => { 
                                this.buffers.stdout.push(s); 
                            }, 
                            stderr: (s) => { 
                                this.buffers.stderr.push(s); 
                            }
                        });
                        resolve(webR);
                    }
                }, 50);
            });
        }
        return this.webRPromise;
    }

    /** Get the contents of the last line of STDOUT, or '' if STDOUT is empty.
     * @returns {string}
     */
    last_stdout_line() {
        return this.buffers.stdout.length == 0 ? '' : this.buffers.stdout[this.buffers.stdout.length-1];
    }

    get stdout() {
        return this.buffers.stdout.join('\n');
    }

    get stderr() {
        return this.buffers.stderr.join('\n');
    }

    run_code(code, namespace_id) {
        const job = this.new_job();
        this.clear_buffers();

        if(namespace_id !== undefined) {
            code = `with(${this.namespace_name(namespace_id)}, {\n${code}\n})`;
        }

        this.load_webR().then(async (webR) => {
            try {
                const result = await webR.runRAsync(code);
                if(result===-1) {
                    throw(new Error(_("Error running R code")));
                } else {
                    job.resolve({
                        result: this.last_stdout_line() === "[1] TRUE",
                        stdout: this.stdout,
                        stderr: this.stderr,
                    });
                }
            } catch(err) {
                this.buffers.stderr.push(err);
                job.reject({
                    error: err.message,
                    stdout: this.stdout,
                    stderr: this.stderr
                });
            }; 
        });

        return job;
    }
}
register_language_runner('webr', WebRRunner);

var run_code = async function(language, codes) {
    try {
        return await language_runners[language_synonym(language)].run_code_blocks(codes);
    } catch(error_results) {
        return error_results;
    }
}

/** Synonyms for code languages (for when there's more than one way of running a given language)
 */
var languageSynonyms = {
    'python': 'pyodide',
    'r': 'webr'
}

/** Get the canonical name for a language by applying synonyms.
 * @param {string} name
 * @returns {string}
 */
var language_synonym = function(name) {
    return languageSynonyms[name] || name;
}

class RunnableCodeElement extends HTMLElement {
    constructor() {
        super();

        this.language = this.getAttribute('language');

        const template = document.getElementById('runnable-code-template');
        const templateContent = template.content;

        const shadowRoot = this.attachShadow({mode: 'open'});
        shadowRoot.appendChild(templateContent.cloneNode(true));

        this.wrapper = shadowRoot.querySelector('.runnable-code-wrapper');
        this.output_display = shadowRoot.querySelector('.output');
        this.set_state('fresh');

        this.init_editor();

        const run_button = this.run_button = shadowRoot.querySelector('.run-code');
        run_button.addEventListener('click', () => this.run());
    }

    init_editor() {
        const code = this.textContent;
        const codeTag = this.shadowRoot.querySelector('.code');

        this.codeMirror = codemirror_editor(
            this.language,
            {
                doc: code,
                parent: codeTag,
                root: this.shadowRoot,
                onChange: update => this.onChange(update)
            }
        );
    }

    set_state(state) {
        this.state = state;
        this.wrapper.dataset.state = this.state;
    }

    async run() {
        switch(this.state) {
            case 'running':
            case 'running-changed':
                return;
        }

        this.run_button.disabled = true;

        const code = this.codeMirror.state.doc.toString();

        try {
            const result = (await run_code(this.language,[code]))[0];
            let output = result.stdout+result.stderr;
            this.output_display.querySelector('.stdout').textContent = output;
            this.output_display.classList.toggle('has-result', result.result);
            const result_string = result.result ?? '';
            this.output_display.querySelector('.result').textContent = result_string;
        } catch(error) {
            console.error(_`An error occured running code: ${error}`);
        } finally {
            switch(this.state) {
                case 'running-changed':
                    this.set_state('changed');
                default:
                    this.set_state('ran');
            }
            this.run_button.disabled = false;
        };
    }

    onChange() {
        switch(this.state) {
            case 'fresh':
                break;
            case 'running':
                this.set_state('running-changed');
                break;
            default:
                this.set_state('changed');
        }
    }
}
customElements.define("runnable-code", RunnableCodeElement);
