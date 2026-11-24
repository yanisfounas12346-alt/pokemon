# Quatrième intégration expérimentale v7

Contrôles locaux du 24 novembre 2026 sur la copie personnelle BPEF fournie par son propriétaire. Aucune ROM commerciale n'est ajoutée au dépôt.

| Contrôle | Résultat |
| --- | --- |
| CRC32 base française | A3FDCCB1 |
| CRC32 v3 | AE02C03C |
| CRC32 v6 | 24B8C94F |
| CRC32 v7 | C93DC5A4 |
| Taille ROM cible | 32 Mio |
| Taille UPS | 197 675 octets |
| SHA256 UPS | fa4c586ff03d34e1c2264528ee7e055db209c3f5f120136d325e6b1532a578ed |
| Nouvelles répliques depuis v6 | 304 |
| Répliques injectées cumulées depuis v3 | 2 164 |
| Cartes concernées | 248 |
| Application et inversion UPS | Octet pour octet |
| Reconstruction depuis v3 selon le journal | Réussie |

## Sélection des dialogues de combat

Les 1 860 répliques v6 et leurs destinations sont conservées. Les commandes trainerbattle sont vérifiées contre la révision source de référence : opcode 0x5C, type de combat, identifiant du Dresseur (constantes opponents.h), identifiant local, position de l'argument texte et concordance des autres arguments texte avec leurs octets originaux. Les commandes dont les octets diffèrent entre base et v3 sont exclues. Les références brutes doivent toutes concorder, la source encodée doit être unique et précédée de FF, la distance commande/texte ne doit pas dépasser 64 Kio et aucune référence intérieure ne doit être détectée. Les nouvelles répliques ne contiennent pas de variable. Les textes de défaite de plus de deux lignes ou dépassant 32 caractères par ligne sont reportés (contrôle indicatif, non pixel). Les types simple, duo, revanche et continuation ont fourni des candidats.

## Suite

2 066 entrées restent hors de cette injection, y compris les entrées identiques et celles déjà intégrées en v3. Il reste notamment des variables dynamiques, des textes partagés, des usages C, des références intérieures possibles et des textes de défaite à relire. Le journal complet est remis séparément. Le patch est expérimental, à appliquer à la ROM originale et non à la v6. Aucun test sur émulateur n'a été effectué : ces contrôles statiques ne garantissent pas le fonctionnement en jeu.
