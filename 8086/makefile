sim8086:
#	python -m sim8086 ./l37
#	python -m sim8086 ./l38
	type l40.asm
	python -m sim8086 ./l40
	python -m sim8086 ./l40 > test.asm
	nasm test.asm
	fc l40 test

wsim8086:
	watchexec -e py -cr "make -B sim8086"
