# Première intégration expérimentale v4

Validation locale du 24 novembre 2026, avec une copie de la ROM fournie par son propriétaire. Aucune ROM n'est ajoutée au dépôt.

- Base BPEF : 16 Mio, CRC32 A3FDCCB1.
- Patch v3 appliqué localement : CRC32 AE02C03C.
- Manifeste : 4 230 dialogues secondaires et 95 narratifs.
- Repérage groupé : 3 823 candidats, 139 sans pointeur exploitable, 47 sources absentes ou ambiguës, 173 textes courts ou partagés, 17 identiques et 31 déjà intégrés à vérifier.
- Sélection expérimentale : 359 nouvelles répliques sur 120 cartes.
- ROM expérimentale : 32 Mio, CRC32 07AB15C8.
- UPS contre la base française : 65 802 octets ; SHA256 820d22fd4b9471ff89edf6b15b972852c14c0819dfdf516ff3e0b4c74891d75e.
- Application et inversion du patch : vérifiées octet par octet.

## Critères de sélection

Texte original unique et inchangé en v3, précédé d'un octet FF, sans variable dynamique ; une seule occurrence de référence dans le script de la carte ; commande msgbox NPC ou SIGN suivie de end, confirmée par les octets 0F 00 [pointeur] 09 02/03 02 ; référence identique dans la base et la v3 ; distance entre script et texte inférieure à 64 Kio ; aucun pointeur brut trouvé vers un octet intérieur du texte. Sur 454 candidats satisfaisant les premiers critères, 95 ont été exclus au contrôle des références intérieures.

Ces vérifications statiques ne remplacent ni une analyse exhaustive des scripts ni des essais en jeu. Le fichier UPS expérimental est remis séparément à l'utilisateur ; il n'est pas publié comme version stable. Les autres dialogues restent à traiter, et les éventuelles références indirectes à inspecter. La ROM commerciale n'est ni téléversée ni distribuée.
