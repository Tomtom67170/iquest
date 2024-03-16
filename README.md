# Quête du QI

## Compilation

### 1. Installer Toga et Briefcase

Quête du QI V2 a été crée avec [Bewware!](https://beeware.org/)!
La compilation du logiciel se fait donc d'une manière très simple avec Briefcase

Nous allons d'abords comment préparer votre terminal à Beeware!
Le tutoriel est également disponible ici <https://docs.beeware.org/fr/latest/tutorial/tutorial-0.html>

Pour éviter tout problème avec votre installation Python, nous vous recommandons fortement de créer un environnement virtuel! Pour ce faire, créer un dossier contenant votre environnement virtuel, puis ouvez-le dans un terminal
    python3 -m venv <nom_du_dossier>

Puis sur Windows:
    <nom_du_dossier>\Scripts\activate

Sur Linux et Mac/OS:
    source <nom_du_dossier>/bin/activate

Enfin, pour installer Briefcase, taper la commande suivante:
    python -m pip install briefcase

### 2. Compiler le projet

La compilation du projet se fait en 2 étapes! Premièrement, assurez-vous d'avoir cloné le dépôt Git du projet, puis rendez-vous dans un terminal, dans le dossier du projet et effectuer les commandes suivantes

    briefcase create
Cette commande va créer un template pour la compilation, à partir du code du projet

    briefcase build
Cette commande va compiler le code en du langague binaire, executable par la machine

### 3. Exploiter ou partager le projet

Pour executer le projet compilé, vous pouvez executer la commande
    briefcase run

Si vous souhaiter en créer un "installateur", effectuer simplement la commande
    briefcase package
Le fichier d'installation de votre machine sera enregistre dans le dossier "dist" à la racine du dossier cloné du projet

## Edition du projet

### Arcitecture des fichiers

Le code source du projet est présent dans le dossier src>iquest>app.py, soit le chemin
    ./src/iquest/app.py

Vous pourrez observer et editer le code à votre guise! Le dossier "resources" dans le dossier de app.py contient différentes ressources utilisé par le logiciel, notamment des images! Certains fichiers .pdn ne sont pas utilisé par le logiciel mais correspondant au fichier image "source" pouvant être lu avec paint.net

Le fichier "pyprojet.toml" présent à la racine du dossier du projet est essentiel, il contient des informations sur le logiciel et peut être modifié avec les paramètres indiqué sur cette [page](https://briefcase.readthedocs.io/en/latest/reference/configuration.html)

### Mise à jour du programme

Si vous modifiez le code source et que vous souhaitez le tester, différentes commandes existent pour cela! Simplement lancer le fichier app.py ne suffit pas...

Si vous souhaiter simplement lancer votre programme à l'aide de votre environnement python de votre machine, vous pouvez lancer le programme avec 
    briefcase dev
Elle lancera le programme avec votre environnement python, avec des logs vous aidant au débuggage

Si vous souhaiter recompiler une nouvelle version du programme, au lieu de faire
    briefcase create

Vous pouvez simplement faire
    briefcase update

Cela va mettre à jour le template de votre programme, ce qui permet l'équivalent de create en étant plus rapide. La suite de la compilation du programme reste la même qu'expliquer précedemment