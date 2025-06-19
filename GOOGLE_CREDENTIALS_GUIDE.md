# Guide pour obtenir des identifiants Google Cloud

## Vue d'ensemble

Cette application utilise deux APIs Google :
- **Google Cloud Vision API** : pour l'analyse d'images
- **Google Gemini API** : pour la génération de métadonnées intelligentes

## Différence entre API Key et Service Account

### 🔑 API Key (Clé API simple)
- **Avantages** : Simple à configurer, idéale pour les tests
- **Inconvénients** : Moins sécurisée, quotas limités
- **Usage** : Projets personnels, prototypage

### 🛡️ Service Account (Compte de service)
- **Avantages** : Plus sécurisé, quotas plus élevés, contrôle granulaire
- **Inconvénients** : Configuration plus complexe
- **Usage** : Applications en production, projets professionnels

## 📋 Étapes pour créer des identifiants

### 1. Créer un projet Google Cloud

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Connectez-vous avec votre compte Google
3. Cliquez sur "Sélectionner un projet" → "Nouveau projet"
4. Donnez un nom à votre projet (ex: "image-auto-tagger")
5. Notez l'**ID du projet** généré automatiquement

### 2. Activer les APIs nécessaires

1. Dans la console, allez dans "APIs et services" → "Bibliothèque"
2. Recherchez et activez :
   - **Cloud Vision API**
   - **Generative Language API** (pour Gemini)

### 3. Créer un compte de service (RECOMMANDÉ)

1. Allez dans "IAM et administration" → "Comptes de service"
2. Cliquez sur "Créer un compte de service"
3. Remplissez :
   - **Nom** : `image-tagger-service`
   - **Description** : `Service account for image auto-tagger application`
4. Cliquez sur "Créer et continuer"
5. Accordez les rôles :
   - `Cloud Vision API User`
   - `AI Platform User` (pour Gemini)
6. Cliquez sur "Continuer" puis "Terminé"

### 4. Télécharger la clé JSON

1. Dans la liste des comptes de service, cliquez sur celui que vous venez de créer
2. Allez dans l'onglet "Clés"
3. Cliquez sur "Ajouter une clé" → "Créer une clé"
4. Sélectionnez "JSON" et cliquez sur "Créer"
5. Le fichier JSON se télécharge automatiquement
6. **IMPORTANT** : Renommez le fichier en `service-account.json`
7. Placez-le dans le dossier `config/` de votre projet

### 5. Configurer les quotas (si nécessaire)

1. Allez dans "APIs et services" → "Quotas"
2. Filtrez par "Vision API" et "Generative Language API"
3. Si vous avez des erreurs de quota, vous pouvez :
   - Demander une augmentation de quota
   - Activer la facturation pour des quotas plus élevés

## 🚨 Résolution des erreurs courantes

### Erreur : "You exceeded your current quota"
**Cause** : Quotas API dépassés
**Solutions** :
1. Vérifiez vos quotas dans la console Google Cloud
2. Activez la facturation pour des quotas plus élevés
3. Attendez la réinitialisation des quotas (généralement quotidienne)

### Erreur : "client_options.api_key and credentials are mutually exclusive"
**Cause** : Conflit entre API key et service account
**Solution** : Cette erreur est maintenant corrigée dans la version mise à jour

### Erreur : "DefaultCredentialsError"
**Cause** : Fichier de credentials introuvable ou invalide
**Solutions** :
1. Vérifiez que le fichier `service-account.json` existe dans `config/`
2. Vérifiez que le fichier n'est pas corrompu
3. Re-téléchargez une nouvelle clé depuis la console

## 💡 Conseils de sécurité

1. **Ne jamais** commiter le fichier `service-account.json` dans Git
2. Ajoutez `config/service-account.json` à votre `.gitignore`
3. Utilisez des variables d'environnement en production
4. Renouvelez régulièrement vos clés
5. Accordez uniquement les permissions minimales nécessaires

## 📊 Surveillance des coûts

1. Activez les alertes de facturation dans Google Cloud
2. Surveillez l'usage des APIs dans "APIs et services" → "Tableau de bord"
3. Définissez des quotas appropriés pour éviter les dépassements

## 🔄 Migration d'API Key vers Service Account

Si vous utilisez actuellement une API key :
1. Suivez les étapes ci-dessus pour créer un service account
2. Supprimez la variable `GEMINI_API_KEY` de votre fichier `.env`
3. Utilisez uniquement le fichier `service-account.json`

---

**Note** : Cette application est maintenant configurée pour utiliser exclusivement les service accounts, ce qui est plus sécurisé et offre de meilleurs quotas.