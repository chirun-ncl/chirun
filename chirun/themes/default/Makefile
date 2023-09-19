RENDERER_THEME=../../plasTeXRenderer/Themes/default

translations/en.po: babel.toml $(wildcard templates/**.html) $(wildcard static/*.*js) $(wildcard $(RENDERER_THEME)/*.jinja2)
	pybabel extract -F babel.toml . $(RENDERER_THEME) -o $@

translations/%.mo: translations/%.po
	msgfmt $< -o $@
