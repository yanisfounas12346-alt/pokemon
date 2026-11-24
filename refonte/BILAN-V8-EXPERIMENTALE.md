# Cinquième intégration expérimentale v8

Contrôles locaux sur la copie personnelle BPEF fournie par son propriétaire. Aucune ROM commerciale n'est ajoutée au dépôt.

| Contrôle | Résultat |
| --- | --- |
| CRC32 base française | A3FDCCB1 |
| CRC32 v3 | AE02C03C |
| CRC32 v7 | C93DC5A4 |
| CRC32 v8 | 158B24FE |
| Taille ROM cible | 32 Mio |
| Taille UPS | 214 063 octets |
| SHA256 UPS | 018758c41885fc689e8ffb9cc61ca9cab04c80d4b043408d95a0573cdc24eb61 |
| Nouvelles répliques depuis v7 | 198 |
| Répliques injectées cumulées depuis v3 | 2 362 |
| Cartes concernées | 262 |
| Application et inversion UPS | Octet pour octet |
| Reconstruction depuis v3 selon le journal | Réussie |

## Critères supplémentaires

Les 2 164 relocations précédentes et leurs destinations sont conservées. Les nouvelles répliques utilisent des commandes msgbox ou message dont les signatures et toutes les références concordent entre la base et la v3. Le premier texte d'une carte est désormais admissible lorsque sa ligne source est comprise entre 1 et 3, que l'octet précédent vaut 02 ou 03 (fin ou retour de script), et que les usages figurent dans le script de cette carte. 126 nouvelles entrées correspondent à cette structure. La recherche impose toujours une source unique et l'absence de pointeur brut intérieur.

84 répliques nouvelles contiennent des variables ou des glyphes. Pour les variables complexes, l'ordre et le nombre des jetons sont conservés et une estimation conservatrice de largeur (16 caractères par variable tampon, au maximum 32 caractères estimés sur les lignes dynamiques) est appliquée. Cette estimation ne constitue pas une mesure de largeur en pixels ni une validation sémantique en jeu.

## Limites

1 868 entrées restent hors de cette injection, dont 31 déjà traitées en v3 à vérifier et 17 identiques. Les références intérieures potentielles, les usages C et les chaînes partagées exigent d'autres contrôles. Aucun émulateur n'est installé dans l'environnement de travail actuel. La v8 reste expérimentale, à appliquer sur la ROM originale et non sur la v7. Le patch et le journal sont remis séparément au propriétaire.
