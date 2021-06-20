**Fév. à mars 2021 – Python : accélération logicielle, prog. parallèle et asynchrone**
- Solution de synchronisation d’un dossier avec un serveur distant à période fixe.
- Transfert parallélisé des fichiers et aucune charge processeur entre deux cycles : développement de threads asynchrones, réveillés « sur front d’horloge » par un dérivé du « 3 way handshake ». Gestion analogue de l’extinction, sans délai.

<br><hr><br>

# M1_S2_parallele_distribue

Python compatibility : 3.6, 3.7, 3.8, 3.9

Note : in your filezilla user settings, change the maximum connection count to 50 or 100

changelog :

#### V0
securize execution:
- already sent folders are excepted
- file transfer send error are excepted


#### V1

**Idea :** apply parallelization principles to ftp operations

Keep algorithm (mainly) unchanged:
- Only modifications : 
    - call any_removals only if "the length of the files & folders to synchronize != number of path explored"
    - add controlled closing meccanism
- Synchronize executions with queue jointures at critical points : 
    - from folder creation to file transfer 
    - from file deletion to folder deletion
- Execute tasks in their detection order (only one queue)


Apply parallelization meccanisms:
- Pass synchronize_directory, search_updates and any_removals asynchrones :
    - while one is awaiting, the other (if called) can carry on
    - sleep time does not cause unnecessary CPU load
- Send tasks to thread pool with an asyncio queue
- Securize concurrency executions by executing enqueue and unqueue operations in same "main thread" async loop
- cascading folders: waits for parent creation or deletion of all items
- Add execution stop : workers stop simultaneously rather than after their sleeping time
- Add try catch bocks : intercept keyboard interrupt where is needed, and set events as needed for provoke ending,
- Add synchronous sleeps between main thread and workers threads with "3 way handshake style" events,
- Add time difference calculation to synchronize late workers with others


**Step1 :**
- synchronize_directory passed async :
    - it await a gather of search_updates and, under condition, any_removals coroutines. Problem here is that without await into coroutine, gather works synchronously
    - it await an asynchrone sleep

**Step2 :**
- synchronize_directory run coroutines concurrently :
    - add little sleep in first coroutine for starting second coroutine
    - add queue synchronisation for after

**Step3 :**
- synchronize_directory run coroutines concurrently :
    - sleep replaced by join() on queue
    - send method name and args to threads and execute them

**Step4 :**
- replace join by wait until empty
- add nb_multi parameter


#### V2

**Idea :** improve parallelization performances with algorithm

change algorithm: 
- Replace jointures by high (folder creation, file deletion) and low (file transfer, folder deletion) priority executions,


**Setp1 :**
- set high and low priority ftp operation queues

**Step2 :**
- synchronize main thread and workers (3way handshake style)
- stop threads at any time if sleeping
- wait for closure of all asyncio running loop threads before finish

**Step3 :**
- temporal synchronization : time diff between thread syn ack and thread ack, moduled by frequency (in case of greater than it), and then, deduced from frequency


#### V3

**Idea :** improve parallelization performances with algorithm

change algorithm: 
- File transfers executions are gathered and sorted by weight before transmit tasks to workers.


**Step1 :**
- sort files transfert by weigth before send them in queue


#### V4

**Idea :** improve performances with test results

change algorithm: 
- Use serialized for removals
- Use parallelized for search updates if enough threads


#### futures versions
- test with process ? probably heavier so worst
- evaluate initial time and execution time separately
- remove priorized queue as we just need to send files : folder creation must be more efficient in synchronous way => need to bench it
- test with threading.lock and threading.queue ? maybe lighter (no await, no run on main loop)
