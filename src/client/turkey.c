#include "turkey.h"

// TODO: write data to shared memory to indicate state (e.g., start / stop)
// TODO: send signal in turkey_destroy to say job completed
TURKEY *turkey_init() {

  TURKEY *client;

  if ((client = (TURKEY *)malloc(sizeof(TURKEY))) == NULL) {
    pexit("Failed to allocate memory for Turkey client");
  }

  client->tshm = turkey_shm_init(getpid());

  Turkey_turkey_shm_data_table_t table = Turkey_turkey_shm_data_as_root(client->tshm->shm);
  client->tshm->data->cpu_shares = Turkey_turkey_shm_data_cpu_shares(table);
  client->tshm->data->cpid = Turkey_turkey_shm_data_cpid(table);
  client->tshm->data->spid = Turkey_turkey_shm_data_spid(table);
  fprintf(stderr, "Got %d share from %d to %d (%d)\n",
          client->tshm->data->cpu_shares,
          client->tshm->data->spid,
          client->tshm->data->cpid,
          getpid()
        );

  fprintf(stderr, "All systems go!\n");

  return client;
}

// TODO: we should call this on failure too
void turkey_destroy(TURKEY *client) {
  turkey_shm_destroy(client->tshm);
  free(client);
}
