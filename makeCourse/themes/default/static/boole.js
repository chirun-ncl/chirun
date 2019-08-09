var opts = {
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
var spinner = new Spinner(opts);
var lastsub = "";
var runnerURL = "https://www.mas.ncl.ac.uk/coderunner";

function waitForSubmission(submissionid,lastCodeDiv){
	setTimeout(function(){
        if(submissionid===undefined){
			return;
		}
		console.log("Checking the status of submission "+submissionid);
		
        $.post(runnerURL, {"@action": "check", "submissionid": submissionid}, null, "json")
            .done(function(data){
                if("status" in data && data['status'] == "waiting"){
                    waitForSubmission(submissionid,lastCodeDiv);
                }else if(data['result'] == "timeout"){
          			console.log("Your job took too long to run");
				}else if(data['result'] == "overflow"){
	        	   	console.log('Your job used too much RAM');    
				}else if(data['result'] == "killed"){
          		   	console.log("Your job was killed");
				} else {
          		    console.log(JSON.stringify(data));
					lastCodeDiv.find('button').removeAttr("disabled").removeAttr('style');
					classes = lastCodeDiv.find('pre').attr("class")
					lastCodeDiv.append("<pre class='ran "+classes+"'><code class='sourceCode'>"+data['stdout']+data['stderr']+"</code></pre>");
					$('div.spinner').remove();
					if (typeof(Reveal) != "undefined"){
						Reveal.layout();
					}
				}
            })
            .fail(function(){
            	console.log("A network error occured");
			});
    }, 1000);
}


function getCodeType(codeClasses){
		var i = codeClasses.indexOf("sourceCode");
		if(i != -1) {
			codeClasses.splice(i, 1);
		}
		var i = codeClasses.indexOf("runnable");
		if(i != -1) {
			codeClasses.splice(i, 1);
		}
		var i = codeClasses.indexOf("editable");
		if(i != -1) {
			codeClasses.splice(i, 1);
		}
		return codeClasses[0];
}

var codeMirrorInstances = {};

//IE Array.includes polyfill
if (!Array.prototype.includes) {
  Object.defineProperty(Array.prototype, 'includes', {
    value: function(searchElement, fromIndex) {
      if (this == null) {
        throw new TypeError('"this" is null or not defined');
      }
      var o = Object(this);
      var len = o.length >>> 0;
      if (len === 0) {
        return false;
      }
      var n = fromIndex | 0;
      var k = Math.max(n >= 0 ? n : len - Math.abs(n), 0);
      function sameValueZero(x, y) {
        return x === y || (typeof x === 'number' && typeof y === 'number' && isNaN(x) && isNaN(y));
      }
      while (k < len) {
        if (sameValueZero(o[k], searchElement)) {
          return true;
        }
        k++;
      }
      return false;
    }
  });
}

$( document ).ready(function() {
	$('div.sourceCode pre.runnable').parent().prepend('<button class="run-code">Run Code »</button>');

	$('div.sourceCode pre code').each(function(){
		preClasses = $(this).parent().attr("class").split(' ');
		codeDir = $(this).parent().parent().data("code-dir");
		gutterSymbol = $(this).parent().parent().data('gutter-symbol');
		if (typeof gutterSymbol === "undefined") {
			gutterSymbol = ">";
		}
		if (typeof(CodeMirror) != "undefined" && !(codeDir == "output")){
			//Codemirror is defined -- we are in normal html land
			randomID = Math.floor(Math.random() * 1000);
			$(this).parent().parent().attr("id","codeMirrorInstance"+randomID);
			$(this).parent().append('<textarea style="width:100%;">'+$(this).text()+'</textarea>');
			var textarea = $(this).parent().find("textarea"); 
			codeClasses = $(this).attr("class").split(' ');
			codeType = getCodeType(codeClasses);
			var codeMirrorOpts = {mode:codeType};
			if (preClasses.includes("editable")){
				codeMirrorOpts["lineNumbers"] = true;
			} else {
				codeMirrorOpts["readOnly"] = true;
			}
			if (codeDir == "input"){
				codeMirrorOpts["lineNumbers"] = true;
				//codeMirrorOpts["lineNumberFormatter"] = function(line){ if (line == 1) { return gutterSymbol; }else{ return "";} };
				codeMirrorOpts["lineNumberFormatter"] = function(line){ return gutterSymbol; };
			}
			var theCodeMirror = CodeMirror.fromTextArea(textarea[0],codeMirrorOpts);
			codeMirrorInstances["codeMirrorInstance"+randomID]=theCodeMirror;
			textarea.remove();
			$(this).remove();
		} else {
			//No Codemirror -- we are in a reveal.js slide
			if (preClasses.includes("editable")){
				$(this).attr('contenteditable','true');
				$(this).attr('spellcheck','false');
			} else {
				if (codeDir == "input"){
					$(this).addClass("code-indented");
					$(this).css("margin-left",5 + 25*gutterSymbol.length);
					$(this).parent().prepend("<span class='code-gutter' style='width: "+(25*gutterSymbol.length)+"px;'>"+gutterSymbol+"&nbsp;<br></span>");
					for (var i = 0; i < 50; i++) {
						var tmp = $(this).parent().find(".code-gutter").html();
						$(this).parent().find(".code-gutter").html(tmp+gutterSymbol+"&nbsp;<br>");
					}
				}
			}
		}
	});

	$('div.sourceCode pre.runnable').on('keydown',function(e){
		$(this).parent().find('pre.ran').remove();
	});

	$('div.sourceCode button.run-code').click(function(e){
		$(this).attr("disabled","disabled").css("background-color","#eeeeee").css("color","#111111");
		lastCodeDiv = $(this).parent();
		lastCodeDiv.find('pre.ran').remove();
		lastCodeDiv.append(spinner.spin().el)
		
		//get code type	
		codeClasses = $(this).next().attr("class").split(' ');
		codeType = getCodeType(codeClasses);

		if($(this).next().children().first().prop("tagName") == "CODE"){
			var br = /<br\s*[\/]?>/gi;
			var codestr = $(this).next().children().first().html();
			var brCleanCodestr = $(this).next().children().first().html(codestr.replace(br, "\n")).text();
			$(this).next().children().first().html(codestr);
			data = {"@action":"getCodeOutput","codetype":codeType+"_getoutput","codeSource":brCleanCodestr};

		} else if($(this).next().children().first().prop("tagName") == "TEXTAREA"){
			data = {"@action":"getCodeOutput","codetype":codeType+"_getoutput","codeSource":$(this).next().children().first().val()};
		} else if($(this).next().children().first().prop("tagName") == "DIV"){
			data = {"@action":"getCodeOutput","codetype":codeType+"_getoutput","codeSource":codeMirrorInstances[$(this).parent().attr("id")].getValue()};
		}
		console.log("Sending message to Inginious:"+JSON.stringify(data))
  		$.post(runnerURL,data,function(returned) {
     		console.log("Got confirmation of message receipt:"+JSON.stringify(returned));
     		lastsub = returned["submissionid"];
     		waitForSubmission(lastsub,lastCodeDiv);
   		});
	});
});