# TP PRAD 2 – Jeu de Devinette Distribué

## Objectif

Créer un jeu client–serveur où :

* **Client 1** choisit un nombre entre 0 et 100.
* **Client 2** doit deviner ce nombre.
* **Le serveur** reçoit le nombre de Client 1 et indique à Client 2 si sa réponse est **Petit**, **Grand** ou **Bravo**.

---

## Fonctionnement

### Serveur

* Attend la connexion de **Client 1** et **Client 2**.
* Reçoit le nombre secret de Client 1.
* Demande à Client 2 de deviner.
* Compare chaque tentative :

  * S > N → « Grand »
  * S < N → « Petit »
  * S == N → « Bravo » et fin du jeu.

---

### Client 1

* Se connecte au serveur.
* Choisit et envoie un nombre entre 0 et 100.

---

### Client 2

* Se connecte au serveur.
* Reçoit l’instruction de deviner.
* Envoie des nombres jusqu’à obtenir « Bravo ».
