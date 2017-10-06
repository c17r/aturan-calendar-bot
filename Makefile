
init:
	@pip install -U pipenv
	@pipenv install --dev

update:
	@pipenv update --dev

flake:
	@pipenv run flake8

test: flake
	@pipenv run py.test -v

coverage: flake
	@pipenv run py.test -v --cov-report term-missing:skip-covered --cov=.

tox:
	@pipenv run tox

readme:
	@pipenv run python -c 'from setup import REPO_USERNAME, NAME; from scripts.utils import make_readme; make_readme(REPO_USERNAME, NAME)'

clean:
	@find -E . -regex ".*\.py[cod]" -delete
	@find -E . -type d -name "__pycache__" -delete
	@find -E . -path "*.egg-info*" -delete
	@[ -d dist ] && rm -r dist/ || true
	@[ -f README.rst ] && rm README.rst || true
	@[ -f .coverage ] && rm .coverage || true

clean-tox: clean
	@[ -d .tox ] && rm -r .tox/ || true

deploy: clean readme
	@pipenv run fab live deploy
