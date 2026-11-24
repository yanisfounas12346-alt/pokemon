# Huitième intégration expérimentale v11

Contrôle local sur la copie personnelle BPEF fournie par le propriétaire. Aucune ROM commerciale ajoutée au dépôt.

| Contrôle | Résultat |
| --- | --- |
| CRC32 base | A3FDCCB1 |
| CRC32 v3 | AE02C03C |
| CRC32 v10 | B2EA0986 |
| CRC32 v11 | 0DA6F2F8 |
| Taille cible | 32 Mio |
| Taille UPS | 295 839 octets |
| SHA256 UPS | ff345931818ee0c6eeaef14208b319524fe229b82bab4cf298cae9ecda018e73 |
| Nouvelles répliques | 308 |
| Total injecté depuis v3 | 3 402 |
| Cartes concernées | 284 |
| Application et inversion UPS | Octet pour octet |
| Reconstruction exacte depuis v3 | Réussie |

## Tour de Combat : partenaires

Dans src/battle_tower.c de la révision de référence, la macro PARTNER_TEXTS assemble cinq pointeurs par partenaire : Intro, Mon1, Mon2Ask, Accept, Reject. Les 66 tables utilisées (16 apprentis et 50 classes) ont été retrouvées sans ambiguïté par comparaison de leurs cinq textes encodés. Les 330 emplacements ont été vérifiés dans la ROM originale et la v3 ; 308 répliques ont passé les critères supplémentaires de source unique, de bornes, de concordance des références, de conservation de la séquence des variables et de largeur estimée (16 caractères par tampon, au plus 32 par ligne). Les questions de partenariat doivent finir par un point d'interrogation.

Les chaînes originales, les 3 094 modifications précédentes et les références intérieures recensées restent intactes. Les 22 autres emplacements de ces tables ne sont pas tous injectés ; certains sont partagés ou ne satisfont pas les critères conservateurs. Il reste 828 entrées hors de cette injection, dont 31 déjà intégrées en v3 à vérifier et 17 identiques.

Le patch v11 s'applique sur la ROM originale, et non sur la v10. La validation est statique : aucune vérification sur émulateur, aucune garantie de rendu en pixels ni de parcours complet. Patch et journal remis séparément au propriétaire.
