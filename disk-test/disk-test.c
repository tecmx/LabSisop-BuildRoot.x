#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>

#define BUFFER_LENGTH 256
#define DISC_SZ	1073741824

int main(){
	int fd;
	char buf[BUFFER_LENGTH] = "Hello World!";

	fd = open("/dev/sdb", O_RDWR);
	if (fd < 0){
		perror("Failed to open the device...");
		return errno;
	}
	
	/* Posicionar-se no inicio do disco. */
	lseek(fd, 0, SEEK_SET);
	
	/* executa leitura. */
	write(fd, buf, strlen(buf));
	
	close(fd);
	
	return 0;
}
