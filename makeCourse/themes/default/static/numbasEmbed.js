function postToFrames(frames, data, origin) {
	for (var i=0; i < frames.length; i++) {
		frames[i].postMessage(data, origin);
		if(frames[i].frames.length > 0) {
			postToFrames(frames[i].frames, data, origin)
		}
	}
}
function storeNumbasScore(frameID, examData) {
	var URL = document.getElementById(frameID).src;
	var key = "numbas_embed:"+URL;
	window.localStorage.setItem(key, JSON.stringify(examData));
	// Check if we're in a CB LTI environment, if so put the score in the KV store
	if(typeof CBLTI !== 'undefined' && CBLTI.user_id){
		console.log("Storing score in KV store at: " + CBLTI.api_path);
		var xhr = new XMLHttpRequest();
		xhr.open("POST", CBLTI.api_path, true);
		xhr.setRequestHeader('Content-Type', 'application/json');
		xhr.send(JSON.stringify({
			'action': 'set',
			'resource_pk': CBLTI.resource_pk,
			'key':	key,
			'value': JSON.stringify(examData)
		}));
	}
}
function updateFeebackBarDisplay(frameID, examData){
	document.getElementById(`${frameID}_score`).innerText = examData.score;
	if(examData.score >= examData.marks){
		document.getElementById(`${frameID}_incomplete`).style.display = "none";
		document.getElementById(`${frameID}_complete`).style.display = "inline-block";
	}
}

function loadNumbasFeedback(frameID){
	var URL = document.getElementById(frameID).src;
	var key = "numbas_embed:"+URL;
	var localExamData = JSON.parse(localStorage.getItem(key));
	
	// Check if we're in a CB LTI environment, if so check the KV store
	if(typeof CBLTI !== 'undefined' && CBLTI.user_id){
		console.log("Getting score from KV store at: " + CBLTI.api_path);
		var req = {
			'action': 'get',
			'resource_pk': CBLTI.resource_pk,
			'key':  key,
		}
		var qs = "";
		for (var key in req) {
			if (qs != "") {
				qs += "&";
			}
			qs += key + "=" + encodeURIComponent(req[key]);
		}
		var xhr = new XMLHttpRequest();
		xhr.onreadystatechange = function() {
			if (xhr.readyState == 4 && xhr.status == 200){
				try {
					var respData = JSON.parse(xhr.responseText);
					var respExamData = JSON.parse(respData['data']);
				} catch (e){
					console.log(e);
					console.log("No valid CBLTI exam data for frameID: "+frameID);
				}
				if((!respExamData && localExamData) || (localExamData && localExamData.score >= respExamData.score)){
					// CBLTI data missing or localstorage is higher
					storeNumbasScore(frameID, localExamData);
					updateFeebackBarDisplay(frameID, localExamData);
				} else if (respExamData){
					// No local data or local data has fewer marks
					storeNumbasScore(frameID, respExamData);
					updateFeebackBarDisplay(frameID, respExamData);
				}
			}
		}
		xhr.open("GET", CBLTI.api_path+'?'+qs, true);
		xhr.send(null);
	} else if(localExamData) {
		storeNumbasScore(frameID, localExamData);
		updateFeebackBarDisplay(frameID, localExamData);
	}
	// Nothing to load
}

function updateNumbasFeedback(frameID, examData){
	var URL = document.getElementById(frameID).src;
	var key = "numbas_embed:"+URL;
	var localExamData = JSON.parse(localStorage.getItem(key));
	if(!localExamData || examData.score >= localExamData.score){
		storeNumbasScore(frameID, examData);
		updateFeebackBarDisplay(frameID, examData);
	}
}

window.addEventListener('message', function(event) {
	var data = JSON.parse(event.data);
	if('message' in data) {
		switch(data['message']){
			case 'height_changed':
				var recvFrameID = data['frame_id'];
				if(recvFrameID){
					document.getElementById(recvFrameID).style.height = parseInt(data.documentHeight+50) + "px";
				}
				break;
			case 'exam_data':
				var recvFrameID = data['frame_id'];
				if(recvFrameID){
					document.getElementById(`${recvFrameID}_marks`).innerText = data.exam.marks;
					document.getElementById(`${recvFrameID}_info`).style.display = "inline-block";
				}
				break;
			case 'part_answered':
				var recvFrameID = data['frame_id'];
				if(recvFrameID){
					updateNumbasFeedback(recvFrameID, data.exam);
					document.getElementById(`${recvFrameID}_info`).style.display = "inline-block";
				}
				break;
			default:
				console.log(data);
		}
	}
});
