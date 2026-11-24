# Treizième intégration expérimentale v16

Validation locale sur la copie BPEF du propriétaire. Aucune ROM commerciale ajoutée au dépôt.

| Contrôle | Résultat |
| --- | --- |
| CRC32 base | A3FDCCB1 |
| CRC32 v15 | F11917AB |
| CRC32 v16 | 35644728 |
| Taille cible | 32 Mio |
| Taille UPS | 324 304 octets |
| SHA256 UPS | 83971db4cf51a74b4e184c338832bed6d38457e1f7332f60b92b5552e005f79c |
| Nouvelles répliques | 60 |
| Total injecté depuis v3 | 3 784 |
| Cartes concernées | 291 |
| Application et inversion UPS | Octet pour octet |
| Reconstruction exacte depuis v3 | Réussie |

Quatre tables complètes de field_specials.c ont été identifiées par correspondance unique de tous les textes encodés, y compris les indices et les répétitions : les 25 natures, les 30 conseils du maniaque du Frontier, et deux tables de 12 conseils chacune. 41 nouvelles répliques sont issues de ces tables, 19 d'une relecture des groupes de pointeurs vérifiés précédemment. Les références sélectionnées, les chaînes originales et les références intérieures recensées sont vérifiées. Les 3 724 injections antérieures sont conservées.

## Audit narratif

Les 95 textes narratifs (84 remplacements et 11 ajouts) sont retrouvés dans la V15 et leurs références concordantes et chaînes cibles restent inchangées dans la V16. Pour 94 textes, toutes les occurrences brutes du pointeur source concordent. Pour le texte AquaExistForGoodOfAll du musée de Poivressel, l'unique usage source msgbox NPC est confirmé par sa signature binaire et pointe vers la réécriture ; deux autres occurrences brutes non identifiées restent intactes. Ceci ne constitue pas une validation exhaustive des usages indirects ni un essai en jeu.

Sur 4 230 répliques secondaires, 3 784 ont été injectées depuis v3 et 47 autres précédemment vérifiées : 399 entrées restent à examiner. Patch expérimental à appliquer sur la ROM originale, non sur la v15. Aucun test sur émulateur.
