# Seizième intégration expérimentale v19

Validation locale sur la copie personnelle BPEF du propriétaire. Aucune ROM commerciale ajoutée au dépôt.

| Contrôle | Résultat |
| --- | --- |
| CRC32 base | A3FDCCB1 |
| CRC32 v18 | F7AAA3AF |
| CRC32 v19 | A43FB89E |
| Taille cible | 32 Mio |
| Taille UPS | 334 396 octets |
| SHA256 UPS | 328ef064197788298f86c20a5d5b4882a384fd8e2e4d1f01304aac25942343a0 |
| Nouvelles répliques | 12 |
| Total injecté depuis v3 | 3 927 |
| Cartes concernées | 291 |
| Application et inversion UPS | Octet pour octet |
| Reconstruction exacte depuis v3 | Réussie |

Dix présentations de partenaires de la Tour de Combat ont été ajoutées en utilisant les tables de cinq pointeurs précédemment identifiées, avec contrôle de la multiplicité des variables et estimation conservatrice des largeurs (80 px pour les noms, 24 pour le numéro à trois chiffres). Deux autres répliques sont identifiées par blocs de textes et signatures de commandes, dont le message d'obtention de Points de Combat : les usages distants sont encadrés par des commandes déjà vérifiées dans chaque fichier source, à moins de 100 lignes et 2 048 octets. Les anciennes chaînes, les 3 915 injections précédentes et les références narratives concordantes sont conservées.

Audit distinct des 81 textes sans usage retrouvé dans l'index source : 61 ont une localisation unique et aucune occurrence brute de pointeur vers la chaîne ou son intérieur en base et en v19 ; 9 ont des occurrences brutes à examiner ; 11 ont une localisation absente ou ambiguë. Aucun de ces 81 textes n'est déclaré inaccessible ni comptabilisé comme injecté sur cette seule base.

3 927 injections et 47 entrées déjà vérifiées, soit 3 974 sur 4 230 traitées ; 256 restent à examiner. Les tests en émulateur ne sont pas réalisés. Patch expérimental à appliquer sur la ROM originale, non sur la v18.
