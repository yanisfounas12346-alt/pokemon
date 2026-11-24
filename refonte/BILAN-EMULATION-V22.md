# Premiers essais réels sur émulateur — V22

Le 24 novembre 2026, compilation de mGBA 0.10.5 à la révision 26b7884bc25a5933960f3cdcd98bac1ae14d42e2 avec le frontal local refonte/emulation/smoke.c. Workflow 45408708407 réussi. Seul le moteur libre a été compilé et transféré par GitHub ; la ROM personnelle est restée locale.

La V22 (CRC32 D6DCDE81) a été obtenue par application du patch UPS à la ROM BPEF originale (A3FDCCB1) et comparée à la ROM de travail. Une séquence de touches a exécuté 17 774 images de jeu. Contrôles visuels réalisés sur les captures : écran titre, nouvelle partie, introduction du professeur Seko, sélection du personnage et du nom de test, camion de déménagement, sortie à Bourg-en-Vol, dialogue réécrit sur le cimetière Nord de Manille et rencontre avec Luzia dans la maison. Le parcours a atteint ces scènes sans blocage observé. Le journal du moteur contient des avertissements d'émulation ; ils ne sont pas tous diagnostiqués. Aucun combat ni sauvegarde/rechargement ni parcours de la Ligue n'a encore été testé.

## Audit des 81 textes

La localisation des 81 textes a été obtenue : 79 par blocs contigus ancrés sur des textes déjà identifiés, 2 par occurrence source unique. La recherche des références brutes vers ces chaînes et leurs octets intérieurs, dans les banques d'adresse 08, 0A et 0C, en base et en V22, donne 64 sans occurrence et 17 avec occurrences à examiner. Dix repères portent explicitement le nom Unused. Ce résultat ne prouve pas l'inaccessibilité des textes ni la nature de chaque occurrence. Aucune injection n'a été effectuée dans cette passe ; la V22 reste inchangée et les 81 entrées ne sont pas comptées comme intégrées.

## Reproduire localement

Compiler le moteur via le workflow dédié, extraire l'artifact et donner les droits d'exécution au binaire gba-smoke. Lancer avec les arguments ROM locale et préfixe de captures, puis fournir sur stdin les couples nombre d'images et masque des touches GBA. Ne pas transférer de ROM dans les workflows. Les captures et la séquence complète ont été remises au propriétaire séparément.
