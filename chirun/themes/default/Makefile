translations/en.po: babel.toml $(wildcard templates/**.html) $(wildcard static/*.*js)
	pybabel extract -F babel.toml . -o $@

translations/%.mo: translations/%.po
	msgfmt $< -o $@
