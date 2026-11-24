# Douzième intégration expérimentale v15

Validation locale sur la copie personnelle BPEF fournie par son propriétaire. Aucune ROM commerciale ajoutée au dépôt.

| Contrôle | Résultat |
| --- | --- |
| CRC32 base | A3FDCCB1 |
| CRC32 v14 | CDFD44F5 |
| CRC32 v15 | F11917AB |
| Taille cible | 32 Mio |
| Taille UPS | 320 027 octets |
| SHA256 UPS | 6c74da36aea799269ccbe76fc851fe9d8d7ad5a93adac7ae87eb927f87e5ce29 |
| Nouvelles répliques | 66 |
| Total injecté depuis v3 | 3 724 |
| Cartes concernées | 291 |
| Application et inversion UPS | Octet pour octet |
| Reconstruction exacte depuis v3 | Réussie |

Les nouvelles répliques remplacent uniquement des chaînes dont les octets en v3 correspondent exactement à la source française encodée après substitution AQUA → MARKS et MAGMA → TRUMPS. Toutes les références directes doivent correspondre aux signatures des commandes et aux usages source, et la chaîne doit être unique parmi les sources secondaires et narratives. Les destinations possibles des textes narratifs sont exclues. Les chaînes originales, les anciennes chaînes renommées et les références intérieures recensées demeurent inchangées. Les entrées nouvelles du journal distinguent source_base et source (destination du texte renommé en v3).

Audit complémentaire : 30 des 31 répliques secondaires signalées comme déjà intégrées en v3 correspondent exactement aux textes attendus via leurs pointeurs ; les 17 entrées identiques ont également été vérifiées. Sur 506 entrées hors injection depuis v3, 47 sont ainsi vérifiées, laissant 459 entrées à examiner. Ce décompte ne couvre pas la validation complète des 95 passages narratifs. Le patch v15 s'applique sur la ROM originale, non sur la v14. Contrôles statiques seulement, aucun essai sur émulateur.
