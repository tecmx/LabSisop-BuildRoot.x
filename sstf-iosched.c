/*
 * SSTF IO Scheduler
 *
 * For Kernel 4.13.9
 */

#include <linux/blkdev.h>
#include <linux/elevator.h>
#include <linux/bio.h>
#include <linux/module.h>
#include <linux/slab.h>
#include <linux/init.h>

sector_t current_position = 0; // Posição atual do cabeçote do disco.

/* SSTF data structure. */
struct sstf_data 
{
	struct list_head queue;
};

static void sstf_merged_requests(struct request_queue *q, struct request *rq,struct request *next)
{
	list_del_init(&next->queuelist);
}

/* Esta função despacha o próximo bloco a ser lido. */
static int sstf_dispatch(struct request_queue *q, int force){
	struct sstf_data *sstd = q->elevator->elevator_data; // Ponteiro para os dados do SSTF, onde está a lista de requisições.
	struct request *rq, *head = NULL; // `rq` para percorrer as requisições, `head` para guardar a requisição mais próxima.
	unsigned long min_distance = ULONG_MAX; // Começamos com a maior distância possível.
	

	// Se houver alguma requisição na lista, usamos a posição do primeiro item como posição inicial.
	// if (!list_empty(&sstd->queue)) {
	// 	current_position = blk_rq_pos(list_first_entry(&sstd->queue, struct request, queuelist));
	// }

	// Itera sobre todas as requisições na lista para encontrar a mais próxima.
	list_for_each_entry(rq, &sstd->queue, queuelist) {
		unsigned long distance = abs(blk_rq_pos(rq) - current_position);
		
		// Se a distância for menor que a menor distância encontrada, atualiza `min_distance` e `head`.
		if (distance < min_distance) {
			min_distance = distance;
			head = rq;
		}
	}

	// Se encontramos uma requisição mais próxima, removemos ela da lista e a despachamos.
	if (head) {
		list_del_init(&head->queuelist); // Remove a requisição da lista.
		elv_dispatch_sort(q, head); // Despacha a requisição para ser processada.
		current_position = blk_rq_pos(head);
		printk(KERN_EMERG "dsp, R, %llu\n", blk_rq_pos(head)); // Loga o setor que está sendo processado.
		return 1; // Retorna 1 para indicar que uma requisição foi despachada.
	}

	return 0; // Retorna 0 se não havia requisições para processar.

	


	/* Aqui deve-se retirar uma requisição da fila e enviá-la para processamento.
	 * Use como exemplo o driver noop-iosched.c. Veja como a requisição é tratada.
	 *
	 * Antes de retornar da função, imprima o sector que foi atendido.
	 */

	
}

static void sstf_add_request(struct request_queue *q, struct request *rq){
	struct sstf_data *sstd = q->elevator->elevator_data;
	char direction = 'R';

	/* Aqui deve-se adicionar uma requisição na fila do driver.
	 * Use como exemplo o driver noop-iosched.c
	 *
	 * Antes de retornar da função, imprima o sector que foi adicionado na lista.
	 */

	list_add_tail(&rq->queuelist, &sstd->queue);
	printk(KERN_EMERG "add, %c, %llu\n", direction, blk_rq_pos(rq));
}

static int sstf_init_queue(struct request_queue *q, struct elevator_type *e){
	struct sstf_data *sstd;
	struct elevator_queue *eq;

	/* Implementação da inicialização da fila (queue).
	 *
	 * Use como exemplo a inicialização da fila no driver noop-iosched.c
	 *
	 */

	eq = elevator_alloc(q, e);
	if (!eq)
		return -ENOMEM;

	sstd = kmalloc_node(sizeof(*sstd), GFP_KERNEL, q->node);
	if (!sstd) {
		kobject_put(&eq->kobj);
		return -ENOMEM;
	}
	eq->elevator_data = sstd;

	INIT_LIST_HEAD(&sstd->queue);

	spin_lock_irq(q->queue_lock);
	q->elevator = eq;
	spin_unlock_irq(q->queue_lock);

	return 0;
}

static void sstf_exit_queue(struct elevator_queue *e)
{
	struct sstf_data *sstd = e->elevator_data;

	/* Implementação da finalização da fila (queue).
	 *
	 * Use como exemplo o driver noop-iosched.c
	 *
	 */
	BUG_ON(!list_empty(&sstd->queue));
	kfree(sstd);
}

/* Infrastrutura dos drivers de IO Scheduling. */
static struct elevator_type elevator_sstf = {
	.ops.sq = {
		.elevator_merge_req_fn		= sstf_merged_requests,
		.elevator_dispatch_fn		= sstf_dispatch,
		.elevator_add_req_fn		= sstf_add_request,
		.elevator_init_fn		= sstf_init_queue,
		.elevator_exit_fn		= sstf_exit_queue,
	},
	.elevator_name = "sstf",
	.elevator_owner = THIS_MODULE,
};

/* Inicialização do driver. */
static int __init sstf_init(void)
{
	printk("op, direction, sector\n");
	return elv_register(&elevator_sstf);
}

/* Finalização do driver. */
static void __exit sstf_exit(void)
{
	elv_unregister(&elevator_sstf);
}

module_init(sstf_init);
module_exit(sstf_exit);

MODULE_AUTHOR("Miguel Xavier");
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("SSTF IO scheduler");