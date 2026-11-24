# Dixième intégration expérimentale v13

Contrôles locaux sur la copie personnelle BPEF fournie par son propriétaire. Aucune ROM commerciale ajoutée au dépôt.

| Contrôle | Résultat |
| --- | --- |
| CRC32 base | A3FDCCB1 |
| CRC32 v3 | AE02C03C |
| CRC32 v12 | F844DE77 |
| CRC32 v13 | 664D4F73 |
| Taille cible | 32 Mio |
| Taille UPS | 308 269 octets |
| SHA256 UPS | 72b15647850c5e327994d2c9ac76f89ed9712e5536d4020104e1d8fd1cc2bc92 |
| Nouvelles répliques | 110 |
| Total injecté depuis v3 | 3 592 |
| Cartes concernées | 284 |
| Application et inversion UPS | Octet pour octet |
| Reconstruction exacte depuis v3 | Réussie |

81 messages ont été identifiés par recherche de la signature de commande et du texte encodé entre deux références mono-usage déjà vérifiées, dans le même fichier source, dans l'ordre des lignes et avec un intervalle maximal de 2 048 octets et 100 lignes source. 29 répliques de combat supplémentaires ont été identifiées par la signature complète de la commande (type, identifiant du Dresseur, identifiant local et textes des autres arguments). Les correspondances multiples, les conflits et les références modifiées en v3 sont exclus. Les variables et contraintes de longueur restent vérifiées suivant les critères conservateurs précédents. Les chaînes originales et références intérieures recensées restent intactes. Les 3 482 entrées précédentes du journal ont été conservées à l'identique.

638 entrées restent hors injection, dont 31 déjà intégrées en v3 à vérifier et 17 identiques. Les vérifications statiques, notamment le repérage par encadrement, ne constituent pas une désassemblage exhaustif des scripts ni un essai en jeu. Le patch expérimental s'applique à la ROM originale, non à la v12. Aucun test sur émulateur effectué.
