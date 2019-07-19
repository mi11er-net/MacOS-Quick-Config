.DEFAULT_GOAL := archive

build_dir := build/
dist_dir := dist/

module_name := quick_config
module_dir := $(module_name)/
module_main_src := $(module_dir)$(module_name).py
module_helpers := __init__.py
module_helpers_src := $(addprefix $(module_dir),$(module_helpers))

app_name := $(subst _,-,$(module_name))
app_relative_dir := $(app_name)/
app_dir := $(dist_dir)$(app_relative_dir)
app_exe := $(app_dir)$(app_name)
app_archive := $(dist_dir)$(app_name).tar.gz


.PHONY: app archive clean lint test

$(app_exe): $(module_main_src) $(module_helpers_src)
	@rm -rf $(app_dir)
	@pipenv run pyinstaller -n $(app_name) $(module_main_src)

$(app_archive): $(app_exe)
	@tar -czvf $(app_archive) -C $(dist_dir) $(app_relative_dir)

app: $(app_exe)

archive: $(app_archive)

clean:
	@rm -rf $(build_dir)
	@rm -rf $(dist_dir)
	@rm -f *.spec
	@rm -f .coverage
	@rm -rf htmlcov/

lint:
	@pipenv run pylint $(module_dir)

test:
	@pipenv run mamba
