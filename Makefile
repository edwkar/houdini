.PHONY: test
test:
	cd test && python test_a.py 
	cd test && python test_b.py 
	cd test && pypy test_a.py 
	cd test && pypy test_b.py 

.PHONY: clean
clean:
	find . -name "*.pyc" | xargs rm -f

