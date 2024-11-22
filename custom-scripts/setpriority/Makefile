BUILDROOT_DIR := ../..
COMPILER := $(BUILDROOT_DIR)/output/host/bin/i686-buildroot-linux-gnu-gcc

all:
	$(COMPILER) -o setpriority setpriority.c
	cp setpriority $(BUILDROOT_DIR)/output/target/bin

clean:
	rm -f setpriority
