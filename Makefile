.PHONY: test
test: development
	tox

development: venv/bin/activate
venv/bin/activate: requirements-dev-minimal.txt
	test -d venv || virtualenv venv
	venv/bin/pip install -r requirements-dev-minimal.txt
	touch venv/bin/activate
