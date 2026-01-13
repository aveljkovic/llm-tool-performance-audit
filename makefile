.PHONY: install run clean

install:
	pip install -r requirements.txt

run:
	python main.py

run-heavy:
	python main.py --tools 100

test:
	python -m unittest discover tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +