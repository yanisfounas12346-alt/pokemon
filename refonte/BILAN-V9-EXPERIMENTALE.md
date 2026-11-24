# Sixième intégration expérimentale v9

Validation locale sur la copie BPEF fournie par le propriétaire ; aucune ROM commerciale ajoutée au dépôt.

| Contrôle | Résultat |
| --- | --- |
| CRC32 base française | A3FDCCB1 |
| CRC32 v3 | AE02C03C |
| CRC32 v8 | 158B24FE |
| CRC32 v9 | 5DD3513E |
| Taille ROM cible | 32 Mio |
| Taille UPS | 270 518 octets |
| SHA256 UPS | b2052ee1958eb52ca3941b52da57039b575028a7497b2e143e39b565c0e5a974 |
| Nouvelles répliques depuis v8 | 554 |
| Répliques injectées cumulées depuis v3 | 2 916 |
| Cartes concernées | 283 |
| Application et inversion UPS | Octet pour octet |
| Reconstruction exacte depuis v3 selon le journal | Réussie |

## Traitement des références intérieures

Cette étape reprend les candidats auparavant exclus en raison d'occurrences brutes de pointeurs vers l'intérieur d'une chaîne. Les commandes directes msgbox et message sont contrôlées comme dans la v8 : texte original unique, nombre et type des références concordants entre sources et ROM, signatures inchangées depuis la base, bornes et variables contrôlées.

Les nouvelles chaînes sont déplacées dans l'extension sans effacer les originales. Le contrôle final vérifie que tous les octets des chaînes originales des 2 916 entrées, ainsi que les octets des occurrences brutes intérieures signalées pour les nouveaux candidats, restent identiques à la v3. Il n'est donc pas nécessaire d'interpréter ces occurrences comme de véritables pointeurs pour conserver leurs destinations. Si un usage indirect existe réellement, il peut toujours afficher le texte d'origine. Cette méthode ne démontre pas une couverture exhaustive de tous les usages.

85 nouvelles répliques comportent des variables ou des codes. Les 2 362 relocations précédentes sont conservées. 1 314 entrées restent hors injection, dont 31 déjà traitées en v3 à vérifier, 17 identiques, 552 usages hors scripts d'événements et 173 chaînes courtes ou partagées. Les autres cas nécessitent des méthodes distinctes.

Le patch v9 expérimental s'applique à la ROM originale, pas à la v8. Aucun test en émulateur n'a été réalisé ; les contrôles binaires ne garantissent pas le fonctionnement en jeu.
