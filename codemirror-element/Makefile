NODE_BIN=node_modules/.bin

../chirun/themes/default/static/runnable_code.js: runnable-code.terser.mjs
	cp $< $@

runnable-code.terser.mjs: runnable-code.bundle.mjs
	$(NODE_BIN)/terser --compress --mangle -- $< > $@

runnable-code.bundle.mjs: runnable-code.mjs
	$(NODE_BIN)/rollup $< -f es -p @rollup/plugin-node-resolve -o $@

