# V22 expérimentale — solde des usages source identifiés

Validation locale sur la copie BPEF du propriétaire. Aucune ROM commerciale ajoutée au dépôt.

| Contrôle | Résultat |
| --- | --- |
| CRC32 base | A3FDCCB1 |
| CRC32 v21 | 1F9B67AE |
| CRC32 v22 | D6DCDE81 |
| Taille cible | 32 Mio |
| Taille UPS | 347 750 octets |
| SHA256 UPS | f809b11940049f64f76a4419539bc7c5143ced6f26167c003813f32d2f662746 |
| Nouvelles répliques | 37 |
| Total injecté depuis v3 | 4 101 |
| Déjà présentes ou identiques, vérifiées | 48 |
| Cartes avec injections depuis v3 | 291 |
| Application et inversion UPS | Octet pour octet |
| Reconstruction exacte depuis v3 | Réussie |

Les 38 entrées restantes avec usage source identifié ont toutes été traitées : 37 injections et vérification du texte exact de défaite de Phoebe, déjà présent en v3. 20 répliques de scripts ont été identifiées par relecture ciblée des blocs et de leurs commandes, 6 textes renommés en v3 par comparaison normalisée de la mise en page (renommage MARKS/TRUMPS et typographie uniquement), 3 répliques de combat par identifiants et arguments texte, 4 descriptions d'objets par tables contiguës vérifiées, 4 textes appelés en C par chargements Thumb PC-relatifs vers r0 et branches BL concordantes, dont un texte également référencé par deux commandes message. Les références brutes non sélectionnées et les anciennes chaînes restent intactes. La reconstruction à partir de v3 et du journal, les 4 064 entrées précédentes et les références concordantes des 95 passages narratifs ont été contrôlées.

Quatre formulations ont été condensées ou remises en page pour les fenêtres de combat et les variables ; le journal recense les adaptations effectives. Les bornes de largeur dynamique restent des estimations, non des tests de rendu.

4 149 entrées secondaires sur 4 230 sont injectées ou vérifiées, soit 98,1 %. 81 entrées sans usage source retrouvé restent à examiner ; elles ne sont pas déclarées inutilisées ou terminées. Aucun essai en émulateur n'a été réalisé, et le repérage statique ne garantit pas tous les usages indirects. Le patch expérimental est fourni séparément au propriétaire et s'applique sur la ROM originale, non sur la v21.
