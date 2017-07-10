import sys
import os
import re
import makeCourse.pandoc
import makeCourse.latex
import makeCourse.hackmd
import makeCourse.slides
from makeCourse import *

def doFindReplace(mdContents):
	reVimeo = re.compile(r'{%vimeo\s*([\d\D]*?)\s*%}')
	reYoutube = re.compile(r'{%youtube\s*([\d\D]*?)\s*%}')
	reNumbas = re.compile(r'{%numbas\s*([^%{}]*?)\s*%}')
	reSlides = re.compile(r'{%slides\s*([^%{}]*?)\s*%}')

	mdContents = reVimeo.sub('<iframe src="https://player.vimeo.com/video/\1" width="100%" height="360" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>', mdContents)
	mdContents = reYoutube.sub('<iframe width="100%" height="360" src="https://www.youtube.com/embed/\1?ecver=1" frameborder="0" allowfullscreen></iframe>', mdContents)
	mdContents = reNumbas.sub('<iframe width="100%" height="1000px" src="\1" frameborder="0"></iframe>', mdContents)
	mdContents = reSlides.sub('<iframe src="\1" style="overflow:hidden;" width="100%" height="480px" scrolling=no frameborder="0"></iframe>', mdContents)

	return mdContents

def createIndexYAMLheader(course_config):
	header = "---\n"
	header += "title: index\n"
	header += "author: %s\n"%course_config['author']
	header += "links:\n"
	for s in course_config['structure']:
		if isHidden(s): continue
		if s['type'] == 'part':
			header += "    - title: %s\n"%s['title']
			header += "      slug: %s\n"%slugify(s['title'])
			header += "      chapters:\n"
			for ch in s['content']:
				if isHidden(ch): continue
				header += "        -  title: %s\n"%ch['title']
				header += "           slug: %s\n"%slugify(ch['title'])
		if s['type'] == 'chapter':
			header += "    - title: %s\n"%s['title']
			header += "      slug: %s\n"%slugify(s['title'])
	header += "\n---\n\n"
	return header

def createYAMLheader(course_config,obj,part=False):
	header = "---\n"
	header += "title: %s\n"%obj['title']
	header += "author: %s\n"%course_config['author']
	if part:
		header += "part: %s\npart-slug: %s\n"%(part['title'],slugify(part['title']))
		header += "chapters:\n"
		for ch in part['content']:
			if isHidden(ch): continue
			header += "    - title: %s\n"%ch['title']
			header += "      file: %s_%s.html\n"%(slugify(part['title']),slugify(ch['title']))
			if obj == ch:
				header += "      active: 1\n"
	header +="\n---\n\n"
	return header

def createPartYAMLheader(course_config,obj):	
	header = "---\n"
	header += "title: %s\n"%obj['title']
	header += "author: %s\n"%course_config['author']
	header += "part-slug: %s\n"%(slugify(obj['title']))
	header += "chapters:\n"
	for ch in obj['content']:
		if isHidden(ch): continue
		header += "    - title: %s\n"%ch['title']
		header += "      slug: %s\n"%slugify(ch['title'])
	header += "\n---\n\n"
	return header

def buildpartMDFile(course_config,part):
	newFile = '%s-%s.md'%(os.urandom(2).encode('hex'),slugify(part['title']))
	course_config['tempFiles'].append(newFile)
	newFileContent = createPartYAMLheader(course_config,part)
	f = open(os.path.join(course_config['args'].dir,newFile), 'w')
	f.write(newFileContent)
	f.close()
	return newFile

def buildIntroMDFile(course_config,obj):
	newFile = '%s-index.md'%os.urandom(2).encode('hex')
	course_config['tempFiles'].append(newFile)
	newFileContent = createIndexYAMLheader(course_config)

	if course_config['args'].verbose:
		print 'Building index: %s'%newFile

	if obj['source'][-3:] == '.md':
		mdContents = open(os.path.join(course_config['args'].dir,obj['source']), 'r').read()
		if mdContents[:3] != '---':
			print '    Burning in iframes & extras.'
			mdContents = doFindReplace(mdContents)
			newFileContent += '\n\n' + mdContents
		else:
			sys.stderr.write("Error: Markdown file %s contains unsupported YAML header. Please remove the header, I'll make one automatically. Quitting...\n"%obj['source'])
			sys.exit(2)
	elif obj['source'][-4:] == '.tex':
		#TODO: Do latex -> html snippet
		newFileContent += '\n\n' + '# Unimplemented feature...'
	elif re.search(r'[^/\?:\s]+', obj['source']):
		code = re.search(r'([^/\?:\s]+)', obj['source']).group(1)
		mdContents = makeCourse.hackmd.getHackmdDocument(course_config,code)
		mdContents = makeCourse.hackmd.getEmbeddedImages(course_config,mdContents)
		newFileContent += '\n\n' + mdContents
	else:
		sys.stderr.write("Error: Unrecognised source type for index. Quitting...\n")
		sys.exit(2)

	f = open(os.path.join(course_config['args'].dir,newFile), 'w')
	f.write(newFileContent)
	f.close()

	if 'source' not in obj.keys():
		sys.stderr.write("Error: No source defined for introduction... Quitting...\n")
		sys.exit(2)

	return newFile

def buildChapterMDFile(course_config,ch,part=False):
	if 'content' in ch.keys() and 'source' in ch.keys():
			sys.stderr.write("Error: Chapter %s contains both content and source elements; including both is invalid. Quitting...\n"%ch['title'])
			sys.exit(2)

	if 'content' in ch.keys():
		if part:
			newFile = '%s-%s_%s.md'%(os.urandom(2).encode('hex'),slugify(part['title']),slugify(ch['title']))
		else:
			newFile = '%s-%s.md'%(os.urandom(2).encode('hex'),slugify(ch['title']))
		course_config['tempFiles'].append(newFile)
		newFileContent = createYAMLheader(course_config,ch,part)

		if course_config['args'].verbose:
			print 'Building chapter file: %s'%newFile

		for sec in ch['content']:
			if isHidden(sec): continue
			if sec['type'] == "section":
				if sec['source'][-3:] == '.md':
					if course_config['args'].verbose:
						print '    Adding: %s'%sec['title']
					mdContents = open(os.path.join(course_config['args'].dir,sec['source']), 'r').read()
					if mdContents[:3] == '---':
						if course_config['args'].verbose:
							print '    Note: Markdown file %s contains a YAML header.'%sec['source']
						mdContents = re.sub(r'^---.*?---\n','',mdContents)
					print '    Burning in iframes & extras.'
					mdContents = doFindReplace(mdContents)
					newFileContent += '\n\n' + '# '+sec['title']+' {.tab-pane .fade}\n' + mdContents
				elif sec['source'][-4:] == '.tex':
					#TODO: Do latex -> html snippet
					newFileContent += '\n\n' + '# '+sec['title']+' {.tab-pane .fade}\nUnimplemented feature...'
				elif re.search(r'[^/\?:\s]+', sec['source']):
					code = re.search(r'([^/\?:\s]+)', sec['source']).group(1)
					mdContents = makeCourse.hackmd.getHackmdDocument(course_config,code)
					mdContents = makeCourse.hackmd.getEmbeddedImages(course_config,mdContents)
					print '    Burning in iframes & extras.'
					mdContents = doFindReplace(mdContents)
					newFileContent += '\n\n' + mdContents
				else:
					sys.stderr.write("Error: Unrecognised source type for %s, %s. Quitting...\n"%(ch['title'],sec['title']))
					sys.exit(2)
			elif sec['type'] == "numbas":
				if course_config['args'].verbose:
					print '    Adding section for numbas: %s'%sec['source']
				newFileContent += '\n\n' + '# '+sec['title']+' {.tab-pane .fade}\n<iframe style="border:none;" height="1000px" width="100%" src="'+sec['source']+'"></iframe>'
			elif sec['type'] == "beamer":
				if sec['source'][-4:] == '.tex':
					if course_config['args'].verbose:
							print '    Adding section for beamer presentation: %s'%sec['title']
					thePDF = makeCourse.latex.runPdflatex(course_config,sec['source'])
					newFileContent += '\n\n' + '# '+sec['title']+' {.tab-pane .fade}\n<object class="loading" data="./static/'+thePDF+'" width="100%" height="500px" type="application/pdf"><embed src="./static/'+thePDF+'"></embed></object>\n<br><p class="pull-right"><a target="_blank" href="./static/'+thePDF+'">Click here to open slides in a new tab<a></p>'
				else:
					sys.stderr.write("Error: Unrecognised source type for %s, %s. Quitting...\n"%(ch['title'],sec['title']))
					sys.exit(2)
			elif sec['type'] == "slideshow":
				if sec['source'][-3:] == '.md':
					if course_config['args'].verbose:
						print '    Adding: %s'%sec['title']
					slideContents = open(os.path.join(course_config['args'].dir,sec['source']), 'r').read()
					if slideContents[:3] == '---':
						if course_config['args'].verbose:
							print '    Note: Markdown file %s contains a YAML header.'%sec['source']
						slideContents = re.sub(r'^---.*?---\n','',slideContents)
					slidesHTMLFile = makeCourse.slides.runPandocForSlides(course_config,sec,slidesEmbedFile)
					newFileContent += '\n\n' + '# '+sec['title']+' {.tab-pane .fade}\n<iframe src="'+slidesHTMLFile+'" width="100%" height="480px" style="overflow:hidden;" scrolling=no frameborder="0"></iframe>'
				elif sec['source'][-4:] == '.tex':
					#TODO: Do latex -> html snippet
					sys.stderr.write("Error: Unimplemented feature... Quitting...\n")
					sys.exit(2)
				elif re.search(r'[^/\?:\s]+', sec['source']):
					code = re.search(r'([^/\?:\s]+)', sec['source']).group(1)
					newFileContent += '\n\n' + '# '+sec['title']+' {.tab-pane .fade}\n<iframe src="'+HACKMD_URL+'/'+code+'/slide" width="100%" height="480px" scrolling=no frameborder="0"></iframe>\n\n<a href="'+HACKMD_URL+'/'+code+'/slide" target="_blank">Open Fullscreen</a>&nbsp;<a href="'+HACKMD_URL+'/'+code+'/pdf" target="_blank">Download PDF</a>'
				else:
					sys.stderr.write("Error: Unrecognised source type for %s, %s. Quitting...\n"%(ch['title'],sec['title']))
					sys.exit(2)
			elif sec['type'] == "vimeo":
				#TODO: include a section for a vimeo video
				newFileContent += '\n\n' + '# '+sec['title']+' {.tab-pane .fade}\n<iframe src="https://player.vimeo.com/video/'+str(sec['source'])+'" width="100%" height="360" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>'
			else:
				sys.stderr.write("Error: Unrecognised section type for %s, %s. Quitting...\n"%(ch['title'],sec['title']))
				sys.exit(2)

		f = open(os.path.join(course_config['args'].dir,newFile), 'w')
		f.write(newFileContent)
		f.close()

	if 'source' in ch.keys():
		if part:
			newFile = '%s-%s_%s.md'%(os.urandom(2).encode('hex'),slugify(part['title']),slugify(ch['title']))
		else:
			newFile = '%s-%s.md'%(os.urandom(2).encode('hex'),slugify(ch['title']))
		course_config['tempFiles'].append(newFile)
		newFileContent = createYAMLheader(course_config,ch,part)

		if course_config['args'].verbose:
			print 'Building chapter file: %s'%newFile

		if ch['source'][-3:] == '.md':
			if course_config['args'].verbose:
				print '    Adding: %s'%ch['title']
			mdContents = open(os.path.join(course_config['args'].dir,ch['source']), 'r').read()
			if mdContents[:3] == '---':
				if course_config['args'].verbose:
					print '    Note: Markdown file %s contains a YAML header. Stripping it...'%ch['source']
				mdContents = re.sub(r'^---.*?---\n','',mdContents,re.S)
			print '    Burning in iframes & extras.'
			mdContents = doFindReplace(mdContents)
			newFileContent += '\n\n' + mdContents
		elif ch['source'][-4:] == '.tex':
			#TODO: Do latex -> html snippet
			newFileContent += '\n\nUnimplemented feature...'
		elif re.search(r'[^/\?:\s]+', ch['source']):
			code = re.search(r'([^/\?:\s]+)', ch['source']).group(1)
			mdContents = makeCourse.hackmd.getHackmdDocument(course_config,code)
			mdContents = makeCourse.hackmd.getEmbeddedImages(course_config,mdContents)
			print '    Burning in iframes & extras.'
			mdContents = doFindReplace(mdContents)
			newFileContent += '\n\n' + mdContents
		else:
			sys.stderr.write("Error: Unrecognised source type for %s:%s. Quitting...\n"%(ch['title'],ch['source']))
			sys.exit(2)

		f = open(os.path.join(course_config['args'].dir,newFile), 'w')
		f.write(newFileContent)
		f.close()

	return newFile

def doProcess(course_config):
	if course_config['args'].verbose:
		print 'Exploring Structure...'

	for obj in course_config['structure']:
		if isHidden(obj): continue
		if obj['type'] == 'introduction':
			obj['title'] = 'index'
			inFileName = buildIntroMDFile(course_config,obj)
			makeCourse.pandoc.runPandocForIntro(course_config,obj,inFileName)
		elif obj['type'] == 'part':
			partFileName = buildpartMDFile(course_config,obj)
			makeCourse.pandoc.runPandocForPart(course_config,obj,partFileName)
			for ch in obj['content']:
				if(ch['type'] != 'chapter'):
					sys.stderr.write("Error: Parts must contain chapters. (%s) Quitting...\n"%obj['title'])
					sys.exit(2)
				course_config['partsEnabled'] = True
				if isHidden(obj): continue
				chFileName = buildChapterMDFile(course_config,ch,part=obj)
				makeCourse.pandoc.runPandocForChapter(course_config,ch,chFileName)
		elif obj['type'] == 'chapter':
			if course_config['partsEnabled']:
				sys.stderr.write("Error: Both parts and chapters found at top level. To fix: put all chapters inside parts or don't include parts at all. Quitting...\n")
				sys.exit(2)
			chFileName = buildChapterMDFile(course_config,ch)
			makeCourse.pandoc.runPandocForChapter(course_config,ch,chFileName)
		elif obj['type'] == 'mocktest':
			#TODO: build a mock test numbas page!
			sys.stderr.write("Error: Unimplemented feature... Quitting...\n")
			sys.exit(2)

	if course_config['args'].verbose:
		print 'Done!'