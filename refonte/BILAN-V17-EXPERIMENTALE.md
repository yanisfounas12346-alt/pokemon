# Quatorzième intégration expérimentale v17

Validation locale sur la copie BPEF du propriétaire. Aucune ROM commerciale ajoutée au dépôt.

| Contrôle | Résultat |
| --- | --- |
| CRC32 base | A3FDCCB1 |
| CRC32 v16 | 35644728 |
| CRC32 v17 | 2EDA94D8 |
| Taille cible | 32 Mio |
| Taille UPS | 329 825 octets |
| SHA256 UPS | 4120ecbe5fd9448d7959d7bda9a60a7338a2d5027da24ed47d4ed1e77ab660db |
| Nouvelles répliques | 76 |
| Total injecté depuis v3 | 3 860 |
| Cartes concernées | 291 |
| Application et inversion UPS | Octet pour octet |
| Reconstruction exacte depuis v3 | Réussie |

28 répliques de combat et 48 répliques de scripts supplémentaires. La table de largeur de la police normale française a été localisée par sa signature source unique à l'offset 6652440 et ses 256 premiers octets comparés entre base et v3. Les lignes statiques sont limitées à 200 pixels (196 pour les textes de défaite, deux lignes maximum). Pour les tampons dynamiques, comparaison à une ligne originale de mêmes variables dans le même ordre et contribution fixe non augmentée ; les noms du joueur et du rival utilisent une estimation conservatrice. Les répétitions de variables peuvent être réduites sans supprimer de variable distincte. Les neuf confirmations oui/non précédemment écartées sont intégrées après comparaison avec les formulations déclaratives originales. Les nouvelles commandes de message sont vérifiées avec leurs opcodes source. Les 3 784 entrées antérieures du journal sont inchangées, les chaînes originales et références intérieures recensées sont conservées ; les références narratives concordantes et leurs textes cibles sont vérifiés inchangés.

Sur 4 230 entrées secondaires, 3 860 injectées depuis v3 et 47 déjà vérifiées, soit 3 907 traitées et 323 restant à examiner. Mesures de largeur statiques, pas de garantie de rendu dynamique ni de fonctionnement en jeu. Aucun test sur émulateur. Patch expérimental à appliquer sur la ROM originale, non sur la v16.