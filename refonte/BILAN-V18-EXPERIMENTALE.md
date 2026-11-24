# Quinzième intégration expérimentale v18

Validation locale sur la copie BPEF du propriétaire. Aucune ROM commerciale ajoutée au dépôt.

| Contrôle | Résultat |
| --- | --- |
| CRC32 base | A3FDCCB1 |
| CRC32 v17 | 2EDA94D8 |
| CRC32 v18 | F7AAA3AF |
| Taille cible | 32 Mio |
| Taille UPS | 333 628 octets |
| SHA256 UPS | 981959235b5ae7e947c43f69ccf4a23acbe2b218fd710181bba2d8e1aba5d967 |
| Nouvelles répliques | 55 |
| Total injecté depuis v3 | 3 915 |
| Cartes concernées | 291 |
| Application et inversion UPS | Octet pour octet |
| Reconstruction exacte depuis v3 | Réussie |

54 répliques sont identifiées par correspondance unique dans la ROM de trois textes consécutifs, distincts, selon leur ordre source, dont au moins un à une adresse déjà vérifiée. Les signatures et le nombre des commandes de dialogue doivent correspondre exactement aux usages source. Une autre réplique a été identifiée par sa source unique et ses références directes, en conservant les occurrences brutes non reconnues. Les chaînes originales et les références intérieures ou non sélectionnées sont inchangées ; les contrôles de variables et de largeur de police de la v17 sont conservés. Le journal précédent et les 95 textes narratifs avec leurs références concordantes sont préservés.

Sur 4 230 entrées secondaires, 3 915 injectées et 47 déjà vérifiées, soit 3 962 traitées et 268 restant à examiner. Le relevé précédent compte notamment 81 textes sans usage retrouvé dans les sources, ce qui ne prouve pas leur absence en jeu. Aucun essai sur émulateur. Le patch expérimental s'applique sur la ROM originale, non sur la v17.
