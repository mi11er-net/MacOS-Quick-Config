.DEFAULT_GOAL := archive

build_dir := build/
app_name := quick-config
dist_dir := dist/
src_dir := $(app_name)/
app_relative_dir := $(app_name)/
app_dir := $(dist_dir)$(app_relative_dir)
app_exe := $(app_dir)$(app_name)
app_archive := $(dist_dir)$(app_name).tar.gz
app_main_src := $(src_dir)$(app_name).py
app_helpers := __init__.py
app_helpers_src := $(addprefix $(src_dir),$(app_helpers))



.PHONY: app archive clean clean_app

$(app_exe): $(app_main_src) $(app_helpers_src)
	@rm -rf $(app_dir)
	@pipenv run pyinstaller $(app_main_src)

$(app_archive): $(app_exe)
	@tar -czvf $(app_archive) -C $(dist_dir) $(app_relative_dir)

app: $(app_exe)

archive: $(app_archive)

clean:
	@rm -rf $(build_dir)
	@rm -rf $(dist_dir)
	@rm -f *.spec


