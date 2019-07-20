.DEFAULT_GOAL := archive

##
# Build Variables
##

build_dir := build/
dist_dir := dist/

build_env_file := $(build_dir)pip

module_name := quick_config
module_dir := $(module_name)/
module_main_src := $(module_dir)__main__.py
module_helpers := __init__.py helpers.py
module_helpers_src := $(addprefix $(module_dir),$(module_helpers))

version_file := $(module_dir)/_version.py
version := $(shell utils/semtag getcurrent)
define version_string
"""
  Version info
"""

__version__ = "$(version)"
endef


app_name := $(subst _,-,$(module_name))
app_relative_dir := $(app_name)/
app_dir := $(dist_dir)$(app_relative_dir)
app_exe := $(app_dir)$(app_name)
app_archive := $(dist_dir)$(app_name).tar.gz

##
# File Targets
##

$(app_exe): $(module_main_src) $(module_helpers_src) $(version_file)
	@rm -rf $(app_dir)
	@pipenv run pyinstaller -n $(app_name) -p $(module_dir) $(module_main_src)

$(app_archive): $(app_exe)
	@tar -czvf $(app_archive) -C $(dist_dir) $(app_relative_dir)

$(version_file): version

# install dependencies into dev environment
$(build_env_file): Pipfile Pipfile.lock
	@pipenv install --dev
	@touch $(build_env_file)

##
# Phony Targets
##

.PHONY: version app archive clean lint test install

export version_string
version:
	@echo "$$version_string" > "$(version_file)"

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

#dev install
install: $(build_env_file)
