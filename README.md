# M1_S2_parallele_distribue

changelog :

#### V1

**Step1 :**
- synchronize_directory passed async :
    - it await a gather of search_updates and, under condition, any_removals coroutines. Problem here is that without await into coroutine, gather works synchronously
    - it await an asynchrone sleep

**Step2 :**
- synchronize_directory run coroutines concurrently :
    - add little sleep in first coroutine for starting second coroutine


#### notes
- décorateur asyncio.coroutine rend fonction synchrone exécutable dans un contexte asynchrone. Mais si la fonction décorée ne fait aucun appel à asyncio, elle est exécutée de façon synchrone.

- mot clé await attend la fin de l'exécution de la coroutine avant de passer à la suite. Donc si coroutine synchrone, fonctionnement purement synchrone.

- tasks n'apporte pas grand chose, mais peut provoquer exécution parallèle avec un micro sleep
