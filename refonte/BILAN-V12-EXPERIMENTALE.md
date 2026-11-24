# Neuvième intégration expérimentale v12

Contrôles locaux sur la copie personnelle BPEF fournie par son propriétaire. Aucune ROM commerciale ajoutée au dépôt.

| Contrôle | Résultat |
| --- | --- |
| CRC32 base | A3FDCCB1 |
| CRC32 v3 | AE02C03C |
| CRC32 v11 | 0DA6F2F8 |
| CRC32 v12 | F844DE77 |
| Taille cible | 32 Mio |
| Taille UPS | 302 207 octets |
| SHA256 UPS | 5fa5287fc46e73faf2bb8c7408df9a6f33368e7cd908482a19bf49e4f6c8d8cf |
| Nouvelles répliques | 80 |
| Total injecté depuis v3 | 3 482 |
| Cartes concernées | 284 |
| Application et inversion UPS | Octet pour octet |
| Reconstruction exacte depuis v3 | Réussie |

68 répliques de combat supplémentaires ont été retenues par validation des commandes trainerbattle, des identifiants et des autres arguments texte ; 45 avaient été exclues en raison de références intérieures et 23 à cause de la borne de début de chaîne. Les chaînes originales et les références intérieures sont conservées. 12 répliques de partenaires supplémentaires ont été intégrées par identification de leurs emplacements précis dans les tables de cinq pointeurs déjà vérifiées, notamment des chaînes partagées ou ambiguës. Les références non sélectionnées demeurent intactes. Les 3 402 relocations antérieures sont conservées.

748 entrées restent hors injection, dont 31 déjà traitées en v3 à vérifier et 17 identiques. Les contrôles sont statiques, sans essai en émulateur. Le patch expérimental fourni au propriétaire s'applique à la ROM originale, non à la v11.
