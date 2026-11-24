# Intégration locale des dialogues BPEF

## État

L'audit logique des textes est distinct de la localisation des données dans une ROM.
Le script `injecter-dialogues.py` est un prototype conservateur. Il ne prouve pas
qu'un candidat trouvé est un véritable texte d'événement : une correspondance
d'octets peut être une fin de chaîne ou une donnée sans rapport. Ne jamais
approuver les candidats automatiquement.

## Prérequis

- Python 3, copie personnelle de Pokémon Émeraude FR, 16 Mio, code BPEF,
  CRC32 `A3FDCCB1`. Ne pas envoyer ni committer cette ROM.
- La référence française de pret/pokeemerald au commit indiqué dans le README,
  avec `charmap.txt`.
- Le manifeste produit par le dernier audit et le patch v3 partiel du dépôt.

## 1. Repérage en lecture seule

Depuis la racine du dépôt :

```sh
python3 refonte/injecter-dialogues.py reperer \
  --rom /chemin/emerald-fr.gba \
  --manifeste rapports/manifeste.json \
  --charmap source-pokeemerald/charmap.txt \
  --sortie rapports/reperage.json
```

Le script contrôle le CRC de la base et ceux du patch UPS v3, applique ce dernier
en mémoire et compare les textes originaux encodés à la ROM. Les dialogues
narratifs et les entrées déjà intégrées à la v3 ne sont pas candidats. Les
textes courts, partagés, ambigus, modifiés ou non encodables nécessitent une
autre méthode de repérage.

## 2. Vérification humaine des adresses

Pour chaque candidat, vérifier dans HexManiacAdvance que le texte débute
réellement à l'offset indiqué, qu'il appartient à la bonne carte et que
**toutes** les occurrences des pointeurs sont de véritables références vers
ce texte. Contrôler notamment les usages indirects, les fragments concaténés,
les menus, les chaînes qui se chevauchent et les dialogues déjà protégés.
Le repérage brut ne décode pas les scripts d'événements.

Construire un fichier d'approbations distinct contenant les quatre empreintes
exactes du repérage et uniquement les entrées validées. Chaque entrée doit
porter les champs `repere`, `offset` (entier décimal), `pointeurs` (liste
d'entiers décimaux), `verification` (description de la vérification humaine).
Ne pas recopier les valeurs d'un autre fichier ou d'une autre ROM.

Commencer par quelques répliques simples. Toute variable modifiée doit
également être relue en contexte, même si le manifeste classe l'écart comme
une répétition ou une suppression de nom.

## 3. Injection expérimentale

```sh
python3 refonte/injecter-dialogues.py injecter \
  --rom /chemin/emerald-fr.gba \
  --manifeste rapports/manifeste.json \
  --charmap source-pokeemerald/charmap.txt \
  --approbations rapports/approbations.json \
  --sortie /chemin/essai-local.gba
```

Le script recalcule le repérage, refuse les approbations périmées et les
pointeurs incomplets. Il déplace les nouveaux textes au-delà des 16 Mio
originaux, produit une copie expérimentale de 32 Mio et un journal JSON des
modifications. Il ne réécrit pas la ROM source et ne fabrique pas encore le
patch UPS final.

Tester chaque dialogue modifié en émulateur, puis les événements qui
l'utilisent. La compatibilité de l'extension et le rendu des caractères restent
à vérifier sur une vraie ROM BPEF.

## 4. Limites

Les tests automatiques utilisent des données artificielles ; ils ne valident
ni les adresses françaises réelles ni le scénario en jeu. Les textes
ambigus, les codes spéciaux non pris en charge et les références indirectes
doivent être traités séparément. Aucun patch complet n'est publié à cette étape.

## 5. Exporter un UPS expérimental vérifié

Après une injection locale réussie, conserver le journal `essai-local.gba.json`
créé par l'injecteur. L'exporteur vérifie la base et la v3, reconstruit les
modifications décrites par le journal et refuse toute modification hors journal.

```sh
python3 refonte/exporter-ups.py \
  --rom /chemin/emerald-fr.gba \
  --rom-injectee /chemin/essai-local.gba \
  --journal /chemin/essai-local.gba.json \
  --sortie /chemin/La-Part-des-absents-experimentale.ups
```

Le patch est calculé contre la ROM d'origine et vérifié dans les deux sens,
octet pour octet, avec contrôle des CRC. Un rapport de vérification JSON
est créé à côté du patch. Ce contrôle de cohérence binaire ne démontre pas
que les pointeurs approuvés sont corrects en jeu ni que tous les textes
sont intégrés. Ne pas publier ce patch comme version finale sans validation
sur émulateur et traitement des repères restants.

## Aide à la relecture des candidats

Le fichier de repérage peut être transformé en une liste de contrôle contenant
le texte d'origine, le nouveau texte, la carte, les offsets et les pointeurs en
décimal et en hexadécimal.

```sh
python3 refonte/preparer-relecture.py preparer \
  --manifeste rapports/manifeste.json --reperage rapports/reperage.json \
  --sortie rapports/relecture.json
```

Aucune entrée n'est préapprouvée. Après inspection dans HMA, renseigner les
trois contrôles, la justification et la décision `approuve` pour chaque
entrée vérifiée. Les entrées non vérifiées restent `a_revoir` ou `refuse`.
Le texte et les adresses ne doivent pas être changés dans ce fichier.

```sh
python3 refonte/preparer-relecture.py valider \
  --manifeste rapports/manifeste.json --reperage rapports/reperage.json \
  --relecture rapports/relecture.json --sortie rapports/approbations.json
```

Cette liste est liée aux empreintes de la ROM originale, de la v3, du manifeste
et de la charmap. Toute modification de ces données impose un nouveau repérage.
Les cases cochées ne prouvent pas une vérification réelle : elles doivent être
renseignées par la personne qui a inspecté les pointeurs, jamais par un
traitement automatique.

## Repères dans les scripts du jeu

Le rapport `usages.json`, généré par l'audit GitHub Actions, donne les
occurrences des identifiants dans les scripts, l'assembleur et le code C
de la révision de référence. Il aide à choisir les premières répliques
à inspecter et à repérer les chaînes susceptibles d'être utilisées hors
d'une boîte de dialogue ordinaire. Un usage unique ne constitue pas une
preuve d'adresse ROM : aucune entrée n'est automatiquement approuvée.
