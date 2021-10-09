const numbas_containers = {};

function postToFrames(frames, data, origin) {
    for (var i=0; i < frames.length; i++) {
        frames[i].postMessage(data, origin);
        if(frames[i].frames.length > 0) {
            postToFrames(frames[i].frames, data, origin)
        }
    }
}

window.addEventListener('message', function(event) {
    try {
        var data = JSON.parse(event.data);
    } catch(e) {
        console.log("Unexpected postMessage data:",event.data);
        return;
    }
    if('message' in data) {
        var recvFrameID = data['frame_id'];
        const n = numbas_containers[recvFrameID];
        switch(data['message']){
            case 'height_changed':
                if(n){
                    n.heightChanged(data);
                }
                break;
            case 'exam_data':
                if(n) {
                    n.receiveExamData(data);
                }
                break;
            case 'part_answered':
                if(n){
                    n.receiveExamData(data);
                }
                break;
            case 'exam_ready':
                setTimeout(function(){
                    for(let n of Object.values(numbas_containers)) {
                        n.sendID();
                    }
                },0);
                break;
            default:
                console.log("Unexpected postMessage data:",data);
        }
    }
});

class NumbasEmbed {
    constructor(container) {
        this.container = container;
        this.id = this.container.getAttribute('data-numbas-id');
        this.url = this.container.getAttribute('data-numbas-url');
        this.storageKey = "numbas_embed:"+this.url;
        this.iframe = this.container.querySelector('.numbas_iframe');
        this.iframe.parentElement.removeChild(this.iframe);

        $(this.container.querySelector('.collapse')).on('show.bs.collapse',() => {
            this.insertEmbed();
        });
    }

    insertEmbed() {
        if(this.iframe.parentElement) {
            return;
        }
        const wrapper = this.container.querySelector('.embed');
        wrapper.appendChild(this.iframe);

        this.iframe.addEventListener('load', () => {
            setTimeout(() => {
                this.loadFeedback();
            },200);
        });
    }

    loadFeedback() {
        var localExamData = JSON.parse(localStorage.getItem(this.storageKey));
        
        // Check if we're in a CB LTI environment, if so check the KV store
        if(typeof CBLTI !== 'undefined' && CBLTI.user_id){
            console.log("Getting score from KV store at: " + CBLTI.api_path);
            var req = {
                'action': 'get',
                'resource_pk': CBLTI.resource_pk,
                'key':  this.storageKey,
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
                        console.log("No valid CBLTI exam data for frameID: "+this.id);
                    }
                    this.update(respExamData);
                }
            }.bind(this);
            xhr.open("GET", CBLTI.api_path+'?'+qs, true);
            xhr.send(null);
        } else if(localExamData) {
            this.update(localExamData);
        }
        // Nothing to load
    }

    update(newExamData) {
        // Compare new examdata with localstorage examdata and only apply if the score is better
        var localExamData = JSON.parse(localStorage.getItem(this.storageKey));
        var examData = localExamData && (!newExamData || !('score' in newExamData) || localExamData.score >= newExamData.score) ? localExamData : newExamData;
        this.storeScore(examData);
        this.updateFeedbackBarDisplay(examData);
    }

    storeScore(examData) {
        window.localStorage.setItem(this.storageKey, JSON.stringify(examData));
        // Check if we're in a CB LTI environment, if so put the score in the KV store
        if(typeof CBLTI !== 'undefined' && CBLTI.user_id){
            console.log("Storing score in KV store at: " + CBLTI.api_path);
            var xhr = new XMLHttpRequest();
            xhr.open("POST", CBLTI.api_path, true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify({
                'action': 'set',
                'resource_pk': CBLTI.resource_pk,
                'key':  this.storageKey,
                'value': JSON.stringify(examData)
            }));
        }
    }

    updateFeedbackBarDisplay(examData){
        if(examData.score!==undefined) {
            const complete = examData.score >= examData.marks;
            this.container.classList.toggle('complete', complete);
        }
    }

    sendID() {
        if(!this.iframe) {
            return;
        }
        if(!this.iframe.contentWindow){
            this.iframe.addEventListener("load", function() {
                postToFrames(
                    this.iframe.contentWindow.frames,
                    JSON.stringify({"message":"send_id","id":this.id}),
                    "*"
                );
            }.bind(this));
        } else {
            postToFrames(
                this.iframe.contentWindow.frames,
                JSON.stringify({"message":"send_id","id":this.id}),
                "*"
            );
        }
    }

    heightChanged(data) {
        if(!this.iframe) {
            return;
        }
        this.iframe.style.height = parseInt(data.documentHeight+50) + "px";
    }

    receiveExamData(data) {
        this.container.querySelector('.feedback_right').classList.add('shown');
        this.update(data.exam);
    }
}

$(function() {
    for(let container of document.querySelectorAll('.numbas_container')) {
        const n = new NumbasEmbed(container);
        numbas_containers[n.id] = n;
    }
});
