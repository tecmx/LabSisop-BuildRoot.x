#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <semaphore.h>
#include <sched.h>
#include <unistd.h>
#include <string.h>

#ifndef SCHED_IDLE
#define SCHED_IDLE 5
#endif

#ifndef SCHED_LOW_IDLE
#define SCHED_LOW_IDLE 7
#endif

// Global variables
char *buffer;
int buffer_size;
int buffer_index = 0;
sem_t semaphore;

// The function that each thread is gonna use 
void* thread_function(void* arg) {
    char character = *(char*)arg;

    while (1) {
        // Access the buffer using semaphore to sync
        sem_wait(&semaphore);

        // Verify if there still is space in the buffer 
        if (buffer_index >= buffer_size) {
            sem_post(&semaphore);
            break;
        }
        
        // Log the thread activity
        printf("Thread %c is writing to the buffer at position %d\n", character, buffer_index);

        // Write char in the buffer and increase pointer 
        buffer[buffer_index++] = character;

        sem_post(&semaphore);
        sched_yield(); // Give CPU time to other thread 
    }

    return NULL;
}

// Function to start threads 
void create_threads(int num_threads, int policy) {
    pthread_t threads[num_threads];
    char thread_chars[num_threads];

    // Configure escalation policy 
    struct sched_param param;
    param.sched_priority = (policy == SCHED_FIFO || policy == SCHED_RR) ? 1 : 0;
    if (sched_setscheduler(0, policy, &param) != 0) {
        perror("Error defining the escalation policy");
        exit(1);
    }
    printf("Current scheduling policy: %d\n", sched_getscheduler(0));

    // Creating threads 
    for (int i = 0; i < num_threads; i++) {
        thread_chars[i] = 'A' + i;
        if (pthread_create(&threads[i], NULL, thread_function, &thread_chars[i]) != 0) {
            perror("Error when creating thread");
            exit(1);
        }
    }

    // Wait the conclusion of all threads 
    for (int i = 0; i < num_threads; i++) {
        pthread_join(threads[i], NULL);
    }
}

// Function for post processing the buffer and count executions 
void post_process_buffer(int num_threads) {
    if (buffer_size == 0) {
        printf("Buffer is empty\n");
        return;
    }

    printf("Final buffer:\n%s\n", buffer);

    int *thread_counts = (int *)calloc(num_threads, sizeof(int)); // Array to count execution of each thread
    if (thread_counts == NULL) {
        perror("Error allocating memory for thread counts");
        return;
    }

    // Counting number of execution for each thread
    for (int i = 0; i < buffer_size; i++) {
        if (buffer[i] >= 'A' && buffer[i] < 'A' + num_threads) {
            thread_counts[buffer[i] - 'A']++;
        }
    }

    printf("Post-Processing:\n");
    for (int i = 0; i < num_threads; i++) {
        printf("%c = %d\n", 'A' + i, thread_counts[i]);
    }

    free(thread_counts);
}


int main(int argc, char* argv[]) {
    if (argc != 4) {
        fprintf(stderr, "Use: %s <buffer_size> <num_threads> <policy>\n", argv[0]);
        exit(1);
    }

    // Read arguments 
    buffer_size = atoi(argv[1]);
    int num_threads = atoi(argv[2]);
    int policy;

    // Choosing escalation policy 
    if (strcmp(argv[3], "SCHED_LOW_IDLE") == 0) 
    {
        policy = SCHED_LOW_IDLE; 
    }
    else if (strcmp(argv[3], "SCHED_IDLE") == 0)
    {
        policy = SCHED_IDLE;
    }
    else if (strcmp(argv[3], "SCHED_FIFO") == 0)
    {
        policy = SCHED_FIFO;
    } 
    else if (strcmp(argv[3], "SCHED_RR") == 0)
    {
        policy = SCHED_RR;
    }
    else
    {
        fprintf(stderr, "Invalid escalation policy \n");
        exit(1);
    }

    // buffer + semaphore 
    buffer = (char*)malloc(buffer_size * sizeof(char));
    if (buffer == NULL) 
    {
        perror("Erro ao alocar memória para o buffer");
        exit(1);
    }
    memset(buffer, 0, buffer_size);
    sem_init(&semaphore, 0, 1);

    // creating threads
    create_threads(num_threads, policy);

    // Buffer post processing 
    post_process_buffer(num_threads);

    //Free space
    free(buffer);
    sem_destroy(&semaphore);

    return 0;
}
