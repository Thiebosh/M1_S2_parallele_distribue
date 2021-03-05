# M1_S2_parallele_distribue

changelog :

#### V1

**Idea :** apply parallelization principles to ftp operations

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

**Setp1 :**
- set high and low priority ftp operation queues

**Step2 :**
- synchronize main thread and workers (3way handshake style)
- stop threads at any time if sleeping

Step3 :
- temporal synchronization (time diff between thread syn ack and thread ack deduced from frequency)

Step4 :
- sort files transfert by weigth in auxiliary thread before send them in queue

Step4 :
- stop synchronization at any time ? => already done for workers, usefull for scanner?

#### notes
- décorateur asyncio.coroutine rend fonction synchrone exécutable dans un contexte asynchrone. Mais si la fonction décorée ne fait aucun appel à asyncio, elle est exécutée de façon synchrone.

- mot clé await attend la fin de l'exécution de la coroutine avant de passer à la suite. Donc si coroutine synchrone, fonctionnement purement synchrone.

- tasks n'apporte pas grand chose, mais peut provoquer exécution parallèle avec un micro sleep

- garde les ftp connect et disconnect de synchronize directory car cette connexion sert à consulter l'état de l'arborescence en ligne

- threads = 2 approches :
    - connexion pour exécuter une série de tâches puis déconnexion
    - connexion le temps d'exécuter une tâche puis déconnexion

- threads = plusieurs choses à guetter :
    - remplissage de la queue
    - événement de fermeture
    - éventuellement événement de connexion / déconnexion

- exemple async tasks : https://docs.python.org/3/library/asyncio-queue.html

- aioftp : port 21 par défaut

- asyncio event doit être déclaré et setté dans la même async loop mais il peut être lu depuis d'autres loops. Attention : il s'agit d'une async loop donc pour une application immédiate, doit passer par thread (-> call_soon_threadsafe)

- pour esquiver pb de concurrences avec async lock, run tout dans la main loop (appel de fonction, retourne un future object contenant les résultats)

