init:
	pip install --upgrade -r requirements.lock

requirements:
	pip install --upgrade -r requirements.txt && \
	pip freeze | \
	grep -v 'aturan-calendar-bot' > requirements.lock
