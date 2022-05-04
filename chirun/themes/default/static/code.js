/** 
 * Runnable code blocks in Chirun
 * Based on the Numbas Programming Extension, Newcastle University, 2020-2022
 * https://github.com/numbas/numbas-extension-programming
 * License: Apache License 2.0
 */

var spinner_opts = {
	lines: 13 // The number of lines to draw
	, length: 28 // The length of each line
	, width: 14 // The line thickness
	, radius: 42 // The radius of the inner circle
	, scale: 0.15 // Scales overall size of the spinner
	, corners: 1 // Corner roundness (0..1)
	, color: '#000' // #rgb or #rrggbb or array of colors
	, opacity: 0.25 // Opacity of the lines
	, rotate: 0 // The rotation offset
	, direction: 1 // 1: clockwise, -1: counterclockwise
	, speed: 1 // Rounds per second
	, trail: 60 // Afterglow percentage
	, fps: 20 // Frames per second when using setTimeout() as a fallback for CSS
	, zIndex: 2e9 // The z-index (defaults to 2000000000)
	, className: 'spinner' // The CSS class to assign to the spinner
	, top: '-24px' // Top position relative to parent
	, left: '97%' // Left position relative to parent
	, shadow: false // Whether to render a shadow
	, hwaccel: false // Whether to use hardware acceleration
	, position: 'relative' // Element positioning
}
var spinner;
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
            throw(new Error("Unrecognised job id "+job_id));
        }
        return this.jobs[job_id];
    }

    /** Run some code in this runner, in the given namespace.
     * @param {string} code - The code to run.
     * @param {namespace_id} namespace_id - The ID of the namespace to run the code in.
     * @returns {job}
     */
    run_code(code, namespace_id) {
        throw(new Error("run_code should be implemented."));
    }

    /** Interrupt the execution of a job.
     * @param {job_id} job_id
     */
    interrupt() {
        throw(new Error("This code runner can't be interrupted."));
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
                    throw(new Error("Error running R code"));
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

$(window).on('load', function() {
	$("pre.cm-block[data-runnable='true']").before('<button class="run-code">Run Code &#187;</button>');

	$('pre.cm-block').each(function(){
		if (typeof(Reveal) == "undefined"){
			var codeTag = $(this).find("code")[0];
			var codeMirrorOpts = {value: $(this).find("code").text()};
			codeMirrorOpts["lineNumbers"] = true;
			codeMirrorOpts["mode"] = $(this).data('language');
			codeMirrorOpts["theme"] = "light default";
			var theCodeMirror = CodeMirror(function(elt) {
				codeTag.parentNode.replaceChild(elt, codeTag);
			} ,codeMirrorOpts);
			codeMirrorInstances[$(this).data('uuid')] = theCodeMirror;
		} else {
			$(this).find("code").attr("contenteditable","true");
			$(this).find("code").attr("spellcheck","false");
		}
	});

	$('pre.cm-block').on('keydown',function(e){
			var codeUUID = $(this).data('uuid');
			$('#ran-'+codeUUID).remove();
	});

	if (typeof(Reveal) != "undefined"){
		$('pre.cm-block code').on('input',function(e){
			var codeUUID = $(this).parent().data('uuid');
			$('#ran-'+codeUUID).remove();
			Reveal.layout();
		});
	}

	$('button.run-code').click(function(e){
		$(this).attr("disabled","disabled");
		var codeBlock = $(this).next();
		var codeUUID = codeBlock.data('uuid');
		var codeLang = codeBlock.data('language');
		$('#ran-'+codeUUID).remove();
		spinner_opts.color = $('body').css("color");
		spinner_opts.className = "spinner"+codeUUID;
		spinner = new Spinner(spinner_opts);
		codeBlock.append(spinner.spin().el)
		if (typeof(Reveal) == "undefined"){
			codeText = codeMirrorInstances[codeUUID].getValue();
		} else {
			codeText = codeBlock.find("code")[0].innerText;
		}
		run_code(codeLang,[codeText]).then(result => {
			console.log(JSON.stringify(result));
			codeBlock.prev().removeAttr("disabled").removeAttr('style');
			$('div.spinner'+codeUUID).remove();
			if (typeof(Reveal) == "undefined"){
				codeBlock.append("<pre id='ran-"+codeUUID+"' class='ran'><code class='sourceCode'>"+result[0]['stdout']+result[0]['stderr']+"</code></pre>");
			} else {
				codeBlock.after("<pre id='ran-"+codeUUID+"' class='ran'><code class='sourceCode'>"+result[0]['stdout']+result[0]['stderr']+"</code></pre>");
				Reveal.layout();
			}
		}, error => {
			console.log("An error occured running code: " + error);
		});
	});
});
