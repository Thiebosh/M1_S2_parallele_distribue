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
    - add queue synchronisation for after


#### notes
- décorateur asyncio.coroutine rend fonction synchrone exécutable dans un contexte asynchrone. Mais si la fonction décorée ne fait aucun appel à asyncio, elle est exécutée de façon synchrone.

- mot clé await attend la fin de l'exécution de la coroutine avant de passer à la suite. Donc si coroutine synchrone, fonctionnement purement synchrone.

- tasks n'apporte pas grand chose, mais peut provoquer exécution parallèle avec un micro sleep

- garde les ftp connect et disconnect de synchronize directory car cette connexion sert à consulter l'état de l'arborescence en ligne


#### todo
- retirer sleep de début : si jobs, pause au milieu du premier et second pourra prendre le relai. Attention : asynchrone = une seule file d'exécution remplie au mieux, donc met en sommeil fonctions qui peuvent l'être pour éveiller fonctions qui doivent l'être

- pour rendre le tout plus efficace sans changer trop (pas de lib ftp async), thread principal asynchrone qui enqueue les tâches + pool de threads secondaires asynchrones qui les exécutent

- envoyer aux threads asynchrones nom méthode + arguments pour qu'ils se chargent d'appeler la bonne méthode avec leur propre instance de ftp...
