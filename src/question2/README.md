# Question 2
## Question 2a.

Le principal point faible de mon script de la question 1b est la récupération des départements des meeting points. Pour recupérer cette donnée,
j'utilise une API gratuite du gouvernement français de reverse geocoding et j'enregistre le resultat dans une base SQLite. Cette partie du 
script comporte plusieurs limites :
#### Limite 1 : Utilisation d'une database SQLite
Dans le cadre de l'exercice, j'ai utilisé une base SQLite car c'est une solution que j'ai considéré legère pour me permettre
de l'utiliser comme un cache et de générer un script avec un temps de réponse acceptable. 

Mais cette solution n'est pas adaptée à une réelle mise en production
à cause de sa limite de taille et qu'elle ne soit pas scalable. Elle n'est pas optimisée pour traiter de grand volume de donnée.

J'aurai préféré completer la table ``meeting_points`` dans BigQuery en ajoutant une colonne
``departement_code``. Il peut y avoir deux solutions pour populer cette colonne :
- Soit cette colonne est populée par batch à une fréquence régulière à définir
- Soit cette colonne est populée à chaque insertion d'un nouveau meeting_point.

L'avantage de populer par batch est de faire moins d'appel API mais en contre-partie, il existera un lapse de temps où la donnée de
``departement_code`` n'existera pas encore pour les nouveaux meeting_points

Populer la colonne dès la création d'un meeting_point pallie cet inconvénient mais derrière demandera plus de ressource car 
les appels API se feront point par point. Cette solution est adaptée s'il y a besoin d'avoir le résultat du script en live. 

En implémentant ce script, j'ai plutot visualisé son utilisation par un collaborateur d'Ornikar et donc je fais l'assomption qu'il n'y
a pas de necessité d'avoir l'information du département en direct. La solution de populer par batch me semble dans ce cas être plus approprié.

#### Limite 2 : Utilisation d'une API de reverse geocoding uniquement pour les départements français
L'avantage de l'API de data.gouv est qu'elle est gratuite mais elle possède des limites.

Dans un premier temps, il n'est pas possible de l'utiliser en batch, le reverse géocoding se fait point par point
et dans le cadre d'une internationalisation de la plateforme, cette API ne serait plus adaptée. 

Il faudrait utiliser une autre API comme celle de Google Maps qui sera plus adapté et qui propose plus de fonctionnalité,
tout en gardant un oeil sur le coût.


#### Point à tester
Afin d'améliorer le temps de ma requête SQL, l'utilisation de la fonction `APPROX_COUNT_DISTINCT` peut être approprié. La
valeur retournée ne sera pas necessairement la valeur exacte mais elle permet d'avoir un impact sur la performance.


## Question 2b.

En supposant que le modèle de labelisation a déjà été entrainé, voici les étapes que je propose 
pour mettre à disposition le label des creneaux : 
- Créer, si necessaire, le pipeline qui va regrouper les fonctions permettant de transformer la donnée brute en un format 
de donnée acceptable pour l'entrée du modèle
- Enregistrer le modèle et le mettre à disposition dans un dépot (model repository), en faisant attention à bien versioner le modèle
- Mettre à disposition le modèle et le code d'inférence dans une API
- Ajouter dans BigQuery la colonne qui contiendra la valeur du label 
- A l'insertion de nouveaux créneaux, appeler l'API définie et inserer la prédiction dans la colonne dédiée