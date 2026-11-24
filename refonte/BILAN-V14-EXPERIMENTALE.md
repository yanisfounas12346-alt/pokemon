# Onzième intégration expérimentale v14

Validation locale sur la copie personnelle BPEF fournie par son propriétaire. Aucune ROM commerciale ajoutée au dépôt.

| Contrôle | Résultat |
| --- | --- |
| CRC32 base | A3FDCCB1 |
| CRC32 v3 | AE02C03C |
| CRC32 v13 | 664D4F73 |
| CRC32 v14 | CDFD44F5 |
| Taille cible | 32 Mio |
| Taille UPS | 313 400 octets |
| SHA256 UPS | 5d28ab4407a75515ca43c53551d5fd3bed2e85b26be693411e81ccaabf421d08 |
| Nouvelles répliques | 66 |
| Total injecté depuis v3 | 3 658 |
| Cartes concernées | 288 |
| Application et inversion UPS | Octet pour octet |
| Reconstruction exacte depuis v3 | Réussie |

51 répliques de scripts partagés ou d'événements (dont un appel PokéNav) ont été validées par unicité du texte source, concordance des nombres de pointeurs et signatures d'opcodes dans la base et la v3. La limite de distance de 64 Kio a été levée uniquement pour les scripts partagés explicitement identifiés. 13 répliques de combat de Vermilava ont été intégrées après vérification des identifiants locaux des objets selon l'ordre des objets dans les deux map.json de l'arène, des types de combat et des arguments texte. Deux répliques supplémentaires du Salon de Combat ont été identifiées dans les rangées répétées de la table C des messages du maniaque du Frontier. Les 3 592 modifications précédentes, les chaînes originales et les références intérieures recensées sont conservées.

572 entrées restent hors injection, dont 31 déjà signalées comme intégrées en v3 et 17 identiques. Plusieurs références d'origine ont été modifiées par la v3 et nécessitent une comparaison spécifique avec les textes narratifs avant toute nouvelle injection. Les contrôles sont statiques et non des essais sur émulateur. Patch expérimental à appliquer sur la ROM française originale, non sur la v13.
