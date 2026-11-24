# V24 expérimentale — bande originale des neuf cercles

Onze compositions originales de 16 mesures, cinq pistes chacune, avec mélodies, harmonies et arrangements distincts. Les morceaux de référence cités par le propriétaire ont uniquement orienté l'ambiance ; leurs mélodies et enregistrements ne sont pas réutilisés.

| ID | Zone | Titre | BPM |
|---|---|---|---:|
| 300 | Manille (Bourg-en-Vol) | Manille | 104 |
| 301 | Mérouville | Orgueil | 116 |
| 302 | Myokara | Avarice | 92 |
| 303 | Lavandia | Spoliation | 126 |
| 304 | Vermilava | Indifférence | 78 |
| 305 | Clémenti-Ville | Exploitation | 94 |
| 306 | Cimetronelle | Abandon | 72 |
| 307 | Algatia | Oppression | 100 |
| 308 | Atalanopolis | Hypocrisie | 112 |
| 309 | Éternara et salles/couloirs du Conseil | Trahison | 70 |
| 310 | Panthéon | Les clefs | 84 |

Intégration locale : onze entrées dummy_song_header de la table originale (IDs 300–310), séquences M4A et en-têtes dans l'extension de la V23, banque d'instruments existante à 0x08694F98. 21 en-têtes de cartes réaffectés. Les villes partageant auparavant une musique ont des thèmes distincts. Les anciennes musiques, routes, combats, fanfares et la plupart des intérieurs sont conservés. Les scènes peuvent encore déclencher des musiques d'origine via leurs scripts. Aucun texte modifié.

CRC32 base A3FDCCB1 ; v23 C5255BD8 ; v24 5F255D4E. UPS 362247 octets, SHA256 3a67ab8140d03ce86f2c5f89ba247bd9554f2265060fff04c0743883d1563f06. Application et inversion octet par octet vérifiées, reconstruction depuis V23 limitée aux nouvelles données et aux 32 modifications de pointeurs/IDs. Essai mGBA : 17774 images, jusqu'au dialogue de Luzia, sans blocage observé. Cet essai visuel ne valide pas le rendu sonore ni chaque boucle. Maquettes MP3 générées avec General MIDI, non identiques aux sons GBA ; fichiers MIDI, patch et rapport remis séparément au propriétaire. Le moteur de test est étendu pour capturer l'audio local. Aucune ROM commerciale distribuée.

## Capture sonore réelle

Le moteur avec capture stéréo (workflow 45415292628 réussi) a rejoué la même séquence de 17 774 images sur V23 et V24. Les captures PCM à 32 768 Hz ont chacune 9 750 792 échantillons stéréo. Le signal est identique avant l'arrivée à Manille (contrôles à 10, 100 et 230 s), puis diverge nettement dès l'arrivée à l'extérieur (238 s). La V24 produit un signal non silencieux pendant toute la scène. Un extrait de 40 secondes, entre 241 et 281 s, est remis au propriétaire ; il contient également les effets sonores des dialogues. Ce contrôle confirme la modification audible à Manille, pas la qualité artistique ni les dix autres thèmes en situation réelle.
