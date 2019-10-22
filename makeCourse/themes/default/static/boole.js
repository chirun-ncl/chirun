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
var runnerURL = "https://www.mas.ncl.ac.uk/coderunner";

function waitForSubmission(submissionid,codeBlock){
	setTimeout(function(){
		if(submissionid===undefined){
			return;
		}
		console.log("Checking the status of submission "+submissionid);
		$.post(runnerURL, {"@action": "check", "submissionid": submissionid}, null, "json")
			.done(function(data){
				if("status" in data && data['status'] == "waiting"){
					waitForSubmission(submissionid,codeBlock);
				}else if(data['result'] == "timeout"){
					console.log("Your job took too long to run");
				}else if(data['result'] == "overflow"){
					console.log('Your job used too much RAM');    
				}else if(data['result'] == "killed"){
					console.log("Your job was killed");
				} else {
					console.log(JSON.stringify(data));
					codeBlock.prev().removeAttr("disabled").removeAttr('style');
					$('div.spinner'+codeBlock.data('uuid')).remove();
					if (typeof(Reveal) == "undefined"){
						codeBlock.append("<pre id='ran-"+codeBlock.data('uuid')+"' class='ran'><code class='sourceCode'>"+data['stdout']+data['stderr']+"</code></pre>");
					} else {
						codeBlock.after("<pre id='ran-"+codeBlock.data('uuid')+"' class='ran'><code class='sourceCode'>"+data['stdout']+data['stderr']+"</code></pre>");
						Reveal.layout();
					}
				}
			})
			.fail(function(){
				console.log("A network error occured");
			});
	}, 1000);
}

function recieveRunnerConfirm(codeBlock){
	return function(msg){ 
		console.log("Got confirmation of message receipt:"+JSON.stringify(msg));
		waitForSubmission(msg["submissionid"],codeBlock);
	}
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
		var data = {"@action":"getCodeOutput", "codetype":codeLang+"_getoutput"}
		if (typeof(Reveal) == "undefined"){
			data["codeSource"] = codeMirrorInstances[codeUUID].getValue();
		} else {
			data["codeSource"] = codeBlock.find("code")[0].innerText;
		}
		console.log("Sending message to Inginious:"+JSON.stringify(data));
		$.post(runnerURL,data,recieveRunnerConfirm(codeBlock));
	});
});
