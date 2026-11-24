# V20 expérimentale — traitement du solde

Validation locale sur la copie BPEF du propriétaire. Aucun fichier ROM ajouté au dépôt.

| Contrôle | Résultat |
| --- | --- |
| CRC32 base | A3FDCCB1 |
| CRC32 v19 | A43FB89E |
| CRC32 v20 | 446D66D3 |
| Taille cible | 32 Mio |
| Taille UPS | 341 040 octets |
| SHA256 UPS | 13affab6ccbf741c38da1577da22b44381690ae4b75e0f5d7bf0942545e6b90e |
| Nouvelles répliques | 73 |
| Total injecté depuis v3 | 4 000 |
| Cartes concernées | 291 |
| Application et inversion UPS | Octet pour octet |
| Reconstruction exacte depuis v3 | Réussie |

37 répliques de combat et 36 messages de scripts : 18 par blocs de trois textes, 17 par ancrage de scripts distants, 1 par bloc de deux textes et ancrage. Les signatures de combat sont vérifiées dans la base originale (type, Dresseur, identifiant local et tous les arguments texte) ; les en-têtes de commandes et les références sélectionnées restent identiques en v3. Les scripts distants sont ancrés par des messages uniques vérifiés ; aux extrémités, trois références ordonnées du même côté et une distance maximale de 512 octets sont exigées. 21 textes de défaite ont été adaptés à deux lignes maximum, avec suppression de sauts de page ou condensation du texte. Ces adaptations sont consignées dans le rapport local, et ne sont pas des reproductions intégrales des formulations prévues. Les 3 927 entrées du journal v19 sont conservées à l'identique ; les chaînes originales et références intérieures recensées restent intactes ; les 95 passages narratifs et leurs références concordantes sont préservés.

## Solde des 256 entrées

| État | Nombre |
| --- | ---: |
| Injectées dans v20 | 73 |
| Usage source présent, non résolu | 102 |
| Aucun usage source retrouvé, accessibilité non établie | 81 |
| Total | 256 |

4 000 injections et 47 entrées déjà vérifiées, soit 4 047 sur 4 230 (95,7 %). Les 183 autres ne sont pas déclarées terminées. Aucun essai sur émulateur n'a été réalisé ; les mesures de largeur et les vérifications binaires ne garantissent pas le comportement en jeu. Le patch expérimental est fourni séparément au propriétaire et s'applique sur la ROM originale, non sur v19.
