make:
	python setup.py build install; echo "==smoke_test======:\n"; python test2.py
data:
	python setup.py make_data --generator="../app/polygon_data.py" --polygon-cell="../cache_map.pickle"
