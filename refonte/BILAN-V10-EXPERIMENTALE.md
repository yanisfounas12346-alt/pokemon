# Septième intégration expérimentale v10

Contrôle local sur la copie BPEF fournie par son propriétaire. Aucune ROM commerciale ajoutée au dépôt.

| Contrôle | Résultat |
| --- | --- |
| CRC32 base | A3FDCCB1 |
| CRC32 v3 | AE02C03C |
| CRC32 v9 | 5DD3513E |
| CRC32 v10 | B2EA0986 |
| Taille cible | 32 Mio |
| Taille UPS | 280 507 octets |
| SHA256 UPS | 8368051ba324b0b36ea54c7d29422778e3081ec62ef9512b232b84bcd063e0b6 |
| Nouvelles répliques | 178 |
| Total injecté depuis v3 | 3 094 |
| Cartes concernées | 284 |
| Application et inversion UPS | Octet pour octet |
| Reconstruction exacte depuis v3 | Réussie |

## Tables C

33 suites contiguës de pointeurs ont été identifiées sans ambiguïté. Chaque suite correspond à au moins trois identifiants distincts et les textes cibles correspondent intégralement aux sources originales encodées. Les octets de la table sont identiques dans la ROM de base et la v3. Pour les nouvelles répliques, toutes les références brutes concordent avec les usages recensés hors déclarations extern ; les variables sont conservées et la longueur des lignes est limitée à 32 caractères (contrôle indicatif). Les descriptions du comptoir d'échange sont limitées à deux lignes.

- Pyramide de Combat : 111 nouvelles répliques.
- Tables de field_specials.c : 46.
- Comptoir d'échange : 21.

Les chaînes originales, les 2 916 modifications précédentes et les références intérieures signalées sont conservées. 1 136 entrées restent hors de cette injection, dont 31 déjà intégrées en v3 à vérifier et 17 identiques. Les contrôles statiques ne prouvent pas la couverture exhaustive des usages indirects ni la validité en jeu. Aucun essai en émulateur. Le patch expérimental est fourni séparément au propriétaire et s'applique à la ROM originale, non à la v9.
