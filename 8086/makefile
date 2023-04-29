sim8086:
#	python -m sim8086 ./l37
#	python -m sim8086 ./l38
	type l39.asm
	python -m sim8086 ./l39
	python -m sim8086 ./l39 > test.asm
	nasm test.asm
	fc l39 test

wsim8086:
	watchexec -e py -cr "make -B sim8086"
