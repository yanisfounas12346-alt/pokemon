# Troisième intégration expérimentale v6

Contrôles locaux du 24 novembre 2026 avec la ROM personnelle BPEF fournie par son propriétaire. Aucune ROM commerciale n'est ajoutée au dépôt.

| Contrôle | Résultat |
| --- | --- |
| CRC32 base française | A3FDCCB1 |
| CRC32 v3 | AE02C03C |
| CRC32 v5 | 11D6808F |
| CRC32 v6 | 24B8C94F |
| Taille ROM cible | 32 Mio |
| Taille UPS | 180 843 octets |
| SHA256 UPS | 4a6239ca55dc89488e6683dd745d7116924c02feecd110cb2cc23a321fe97935 |
| Nouvelles répliques depuis v5 | 526 |
| Répliques injectées cumulées depuis v3 | 1 860 |
| Cartes concernées | 245 |
| Application et inversion UPS | Octet pour octet |
| Reconstruction exacte à partir de v3 et du journal | Réussie |

## Critères supplémentaires

Conservation des 1 334 relocations de la v5 aux mêmes adresses. Extension aux commandes msgbox YESNO (type 5), AUTOCLOSE (type 6) et message (opcode 67), ainsi qu'aux scripts d'événement partagés. 371 nouvelles répliques sans variable et 155 avec noms ou suffixes dynamiques, sans introduire de nouvelle variable ni augmenter le nombre d'occurrences. Les autres variables et codes spéciaux sont laissés pour relecture. Les questions oui/non doivent se terminer par un point d'interrogation ; ce contrôle ne prouve pas leur cohérence sémantique. Le contrôle de longueur des noms reste indicatif, pas une mesure de largeur en pixels.

Pour toutes les nouvelles entrées : source encodée unique, inchangée en v3, précédée de FF ; concordance des types, du nombre et des octets des références dans la base et la v3 ; distance entre commande et texte inférieure ou égale à 64 Kio ; absence de références brutes intérieures. Les textes sont ajoutés après les destinations v5, sans écraser les précédents. La comparaison du résultat complet avec la v3 reconstruite selon le journal a réussi.

## Entrées non injectées à cette étape

| Motif | Nombre |
| --- | ---: |
| Référence intérieure possible | 478 |
| Commande ou type non retenu | 452 |
| Variables ou codes à relire | 385 |
| Usage hors script d'événement | 338 |
| Source ou borne non concordante | 228 |
| Texte court ou partagé | 173 |
| Pointeurs absents ou trop nombreux | 139 |
| Signature non concordante | 59 |
| Source absente ou ambiguë | 47 |
| Déjà intégrée en v3, à vérifier | 31 |
| Texte identique | 17 |
| Références non concordantes | 15 |
| Question oui/non à relire | 8 |
| **Total** | **2 370** |

Le patch v6 expérimental est remis séparément à l'utilisateur et s'applique sur la ROM originale, pas sur la v5. Les contrôles statiques ne garantissent pas l'absence de bugs en jeu. Aucun test sur émulateur n'a été effectué et cette version n'est pas présentée comme finale.
