# V21 expérimentale — variables et scripts partagés

Validation locale sur la copie BPEF du propriétaire. Aucune ROM commerciale ajoutée au dépôt.

| Contrôle | Résultat |
| --- | --- |
| CRC32 base | A3FDCCB1 |
| CRC32 v20 | 446D66D3 |
| CRC32 v21 | 1F9B67AE |
| Taille cible | 32 Mio |
| Taille UPS | 345 201 octets |
| SHA256 UPS | 4df3bbbaa29516d35e1db1db50e2407c1c0a831ffda28304e32d5c0c3a13bf09 |
| Nouvelles répliques | 64 |
| Total injecté depuis v3 | 4 064 |
| Cartes concernées | 291 |
| Application et inversion UPS | Octet pour octet |
| Reconstruction exacte depuis v3 | Réussie |

29 répliques sont identifiées par blocs de textes consécutifs, 9 par références directes avec conservation des occurrences brutes non sélectionnées, et 26 par recoupement des scripts partagés. Les signatures des commandes et le nombre de références doivent correspondre aux usages source. Pour les scripts distants, une affectation unique est recherchée selon les ancres vérifiées et l'ordre des commandes ; les fichiers sans ancre proche nécessitent au moins trois autres répliques indépendamment recoupées, dans le même ordre relatif et à moins de 2 048 octets et 100 lignes source. Cette méthode reste une vérification statique, pas un désassemblage exhaustif.

38 nouveaux textes ont été remis en page sans changer les mots, avec conservation des jetons dynamiques prévus, contrôle des largeurs de police, comparaison de la contribution fixe aux lignes sources contenant les tampons et absence de ponctuation seule sur une ligne. Les 21 adaptations v20 sont conservées. L'estimation des tampons ne constitue pas un essai de rendu dynamique.

Les 4 000 entrées du journal v20 sont inchangées ; les chaînes originales, références intérieures recensées et 95 textes narratifs avec leurs références concordantes sont préservés. Sur 4 230 répliques secondaires, 4 064 injectées et 47 déjà vérifiées, soit 4 111 traitées. Restent 38 entrées avec usage source non résolu et 81 sans usage source retrouvé, dont l'accessibilité n'est pas établie. Aucun test sur émulateur. Le patch expérimental s'applique à la ROM originale et non à la v20.
