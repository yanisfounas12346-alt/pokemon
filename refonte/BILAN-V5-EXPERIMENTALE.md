# Deuxième intégration expérimentale v5

Validation locale du 24 novembre 2026. La ROM personnelle BPEF fournie par le propriétaire reste dans l'environnement local et n'est pas ajoutée au dépôt.

| Contrôle | Résultat |
| --- | --- |
| CRC32 de la ROM de base | A3FDCCB1 |
| CRC32 de la v3 | AE02C03C |
| CRC32 de la v4 | 07AB15C8 |
| CRC32 de la v5 expérimentale | 11D6808F |
| Taille ROM cible | 32 Mio |
| Taille UPS | 142 861 octets |
| SHA256 UPS | 4e47872d3f330ecf4e35b2d7a9a4bec0ef1f3de090ef17decd72b33a633647ab |
| Nouveaux dialogues depuis la v4 | 975 |
| Dialogues injectés cumulés depuis la v3 | 1 334 |
| Cartes concernées | 215 |
| Application et inversion UPS | Octet pour octet |
| Reconstruction exacte depuis la v3 et le journal | Réussie |

## Sélection

Les 359 répliques de la v4 sont conservées aux mêmes destinations. Les 975 nouvelles répliques ont été retenues uniquement si leur source encodée est unique, inchangée dans la v3 et précédée de FF, si tous les usages relevés sont des commandes msgbox NPC, SIGN ou DEFAULT du script de la carte, et si les nombres et types de références concordent avec les signatures binaires de la ROM originale et de la v3. Les références brutes, y compris non alignées, ont été indexées ; tout pointeur brut vers l'intérieur de la chaîne entraîne une exclusion. Les textes avec variables ou codes spéciaux ont été laissés pour une étape séparée. Les destinations ont été ajoutées dans la zone d'extension existante ; aucune modification hors des pointeurs journalisés et des textes déplacés n'a été constatée.

## Textes non injectés à cette étape

| Motif de report | Nombre |
| --- | ---: |
| Commande ou type non retenu | 894 |
| Variables ou codes à relire | 669 |
| Usage hors script de la carte | 399 |
| Référence intérieure possible | 345 |
| Texte court ou partagé | 173 |
| Source ou borne non concordante | 171 |
| Pointeurs absents ou trop nombreux | 139 |
| Source absente ou ambiguë | 47 |
| Références non concordantes | 11 |
| Texte identique | 17 |
| Entrée déjà intégrée en v3 à vérifier | 31 |

Ces catégories sont exclusives dans ce relevé et totalisent 2 896 entrées. Elles ne constituent pas toutes des erreurs : certaines exigent une autre méthode de repérage, d'autres sont déjà intégrées ou identiques.

La v5 est un UPS expérimental remis séparément à l'utilisateur, à appliquer sur la ROM BPEF originale, et non sur la v4. Aucune vérification sur émulateur n'a été réalisée ; les contrôles binaires ne prouvent pas le comportement en jeu. Aucune ROM n'est publiée.
