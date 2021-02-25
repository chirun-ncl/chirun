// MP4 Video Fallback
// Based on code by @shshaw: https://codepen.io/shshaw/pen/MOMezY
function mp4ImageFallback() {
	var videoAttr = { 'loop': '', 'autoplay':'', 'muted': '', 'playsinline': '' };
	var imgMP4s = Array.prototype.map.call(
		document.querySelectorAll('img[src*=".mp4"]'),
		function(img){
			var src = img.src;
			img.src = null;
			img.addEventListener('error', function(e){
				console.log('MP4 in image not supported. Replacing with video', e); 
				var video = document.createElement('video');
				for (var key in videoAttr) { video.setAttribute(key, videoAttr[key]); }
				for (
					var imgAttr = img.attributes, 
					len = imgAttr.length,
					i = 0; 
					i < len; 
					i++
				) { 
					video.setAttribute(imgAttr[i].name,  imgAttr[i].value);
					video.muted = true;
				}
				img.parentNode.insertBefore(video, img);
				img.parentNode.removeChild(img);
			});
			img.src = src;
		});
}
try {
	mp4ImageFallback();
} catch(err) {
	console.log('Problem replacing MP4 images: '+err);
}

