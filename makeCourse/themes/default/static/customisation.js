const themeBtns = document.querySelectorAll('#themeSelector > button')

// Load local storage
if(localStorage.getItem("css-font-size")) {
	changeFontSize(localStorage.getItem("css-font-size"))
}
if(localStorage.getItem("theme")) {
	handleThemeUpdate(localStorage.getItem("theme"))
}
if(localStorage.getItem("css-p-space")) {
	changeParagraphSpacing(localStorage.getItem("css-p-space"))
}

for (var i = 0; i < themeBtns.length; i++) {
	themeBtns[i].addEventListener('click', function(e) {
		handleThemeUpdate(e.target.value);
		e.preventDefault();
	});
}

$("#navbarCustomise #font-scale").on("input change", function() {
	changeFontSize(this.value); 
});

$("#navbarCustomise #p-space").on("input change", function() {
	changeParagraphSpacing(this.value);
});

$("#navbarCustomise #font-scale-reset").click(function() {
	changeFontSize(100);
	localStorage.removeItem('css-font-size');
});

$("#navbarCustomise #p-space-reset").click(function() {
	changeParagraphSpacing(150);
	localStorage.removeItem('css-p-space');
});

function updateThemeBodyTag() {
	$('body').attr('data-theme', localStorage.getItem('theme') || 'light');
}

function handleThemeUpdate(theme) {
	if($('#customiseCSS')[0]){
		var t =  $('#customiseCSS')[0].getAttribute('href');
		$('#customiseCSS')[0].setAttribute('href',t.substring(0, t.lastIndexOf("/") + 1)+theme+'.css'); 
	}
	if($('#customiseCodeCSS')[0]){
		var t =  $('#customiseCodeCSS')[0].getAttribute('href'); 
		$('#customiseCodeCSS')[0].setAttribute('href',t.substring(0, t.lastIndexOf("/") + 1)+'pygmentize.'+theme+'.css'); 
	}
	
	// Save in local storage
	localStorage.setItem('theme',theme);
	updateThemeBodyTag();
}

function changeFontSize(fontScale) {
	var fs = fontScale/100;
	$('body > nav').css("font-size", (fs*1.0)+"rem");
	$('body > header').css("font-size", (fs*1.0)+"rem");
	$('body > main').css("font-size", (fs*1.0)+"rem");
	$('.nav .nav > li > a').css("font-size", (fs*0.8)+"rem");
	$('body > footer').css("font-size", (fs*1.0)+"rem");
	$('h1').css("font-size", (fs*2.5)+"rem");
	$('h2').css("font-size", (fs*2.0)+"rem");
	$('h3').css("font-size", (fs*1.5)+"rem");
	$('h4').css("font-size", (fs*1.3)+"rem");
	$('.card-header > h2').css("font-size", (fs*1.3)+"rem");
	//$('body>main .btn').css("font-size", (fs*1.0)+"rem");
	//$('nav[data-toggle="toc"] .nav > li > a').css("font-size", (fs*1.0)+"rem");

	// Update slider display
	$('#font-size-display').text(Math.round(fontScale)+'%')
	$('#font-scale').val(fontScale)

	// Save in local storage
	localStorage.setItem('css-font-size',fontScale);

	// Change some of the layout if large font size
	if(fontScale>150){
		$('#sidebar').removeClass('col-md-3');
		$('#sidebar').addClass('col-md-12');    
		$('#content').removeClass('col-md-9');
		$('#content').addClass('col-md-12');    
		$('main .card-container').addClass('col-md-8');
		$('main .card-container').removeClass('col-md-6');
		$('main .card-container').addClass('col-lg-6');
		$('main .card-container').removeClass('col-lg-4');
	}else{
		$('#sidebar').addClass('col-md-3');
		$('#sidebar').removeClass('col-md-12');      
		$('#content').addClass('col-md-9');
		$('#content').removeClass('col-md-12');      
		$('main .card-container').addClass('col-md-6');
		$('main .card-container').removeClass('col-md-8');
		$('main .card-container').addClass('col-lg-4');
		$('main .card-container').removeClass('col-lg-6');
	}
}

function changeParagraphSpacing(paragraphScale) {
	var ps = paragraphScale/100;
	$('main p').css("margin-bottom", ps+"em");
	$('header .intro-header').css("margin-bottom", Math.max(ps-1.0,0.0)+"em");
	if(paragraphScale >= 100){
		$('main p').css('line-height', ps+"em");
		$('main p').css('line-height', ps+"em");
	}

	// Update slider display
	$('#p-space-display').text(Math.round(paragraphScale)+'%')
	$('#p-space').val(paragraphScale)

	// Save in local storage
	localStorage.setItem('css-p-space',paragraphScale);
}

$(document).ready(() => {
	updateThemeBodyTag(localStorage.getItem('theme'))
});
