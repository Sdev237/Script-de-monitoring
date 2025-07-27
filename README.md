# 🚀 Script de Monitoring Réseau et CPU

Un système de monitoring complet pour surveiller les ressources système (CPU, mémoire, disque, réseau) via SNMP avec alertes automatiques.

## 📋 Fonctionnalités

- **Surveillance SNMP** : Monitoring des ressources système via protocole SNMP
- **Métriques surveillées** :
  - Utilisation CPU
  - Utilisation mémoire RAM
  - Utilisation disque
  - Trafic réseau
- **Système d'alertes** :
  - Seuils configurables (warning/critical)
  - Alertes par email
  - Historique des alertes
- **Interface graphique** : Interface Tkinter pour la configuration et le suivi
- **Rapports** : Génération de rapports et export CSV
- **Logging** : Journalisation complète des événements

## 🛠️ Prérequis

### Système cible (à surveiller)

- SNMP activé et configuré
- Community string configuré (par défaut: "public")
- Accès réseau depuis le système de monitoring

### Système de monitoring

- Python 3.7+
- Bibliothèques Python (voir requirements.txt)

## 📦 Installation

1. **Cloner ou télécharger le projet**

```bash
git clone <repository-url>
cd "Script de monitoring réseau ou CPU"
```

2. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

3. **Configuration SNMP sur les systèmes cibles**

### Linux (Ubuntu/Debian)

```bash
sudo apt-get install snmpd
sudo nano /etc/snmp/snmpd.conf
```

Ajouter/modifier :

```
rocommunity public
agentAddress udp:161
```

Redémarrer le service :

```bash
sudo systemctl restart snmpd
sudo systemctl enable snmpd
```

### Windows

1. Installer les fonctionnalités SNMP via "Ajouter des fonctionnalités Windows"
2. Configurer la communauté SNMP dans les services
3. Ouvrir le port 161/UDP dans le pare-feu

## ⚙️ Configuration

### Configuration automatique

Le script crée automatiquement un fichier `config.json` avec des valeurs par défaut.

### Configuration manuelle

Éditer le fichier `config.json` :

```json
{
  "snmp": {
    "community": "public",
    "timeout": 3,
    "retries": 3
  },
  "targets": [
    {
      "name": "Serveur Principal",
      "ip": "192.168.1.100",
      "port": 161
    }
  ],
  "thresholds": {
    "cpu_warning": 70,
    "cpu_critical": 90,
    "memory_warning": 80,
    "memory_critical": 95,
    "disk_warning": 85,
    "disk_critical": 95,
    "network_warning": 1000000
  },
  "alerts": {
    "email_enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "votre-email@gmail.com",
    "sender_password": "votre-mot-de-passe-app",
    "recipients": ["admin@example.com"]
  },
  "monitoring": {
    "interval": 60,
    "log_file": "monitoring.log"
  }
}
```

## 🚀 Utilisation

### Interface graphique (recommandée)

```bash
python monitoring_ui.py
```

L'interface permet de :

- Configurer les cibles SNMP
- Définir les seuils d'alerte
- Configurer les alertes email
- Démarrer/arrêter le monitoring
- Consulter les métriques en temps réel
- Générer des rapports

### Ligne de commande

```bash
# Démarrage simple
python start_monitoring.py

# Ou directement
python monitoring_system.py
```

### Script principal

```bash
python monitoring_system.py
```

## 📊 OIDs SNMP utilisés

Le script utilise les OIDs SNMP suivants :

| Métrique     | OID                      | Description                       |
| ------------ | ------------------------ | --------------------------------- |
| CPU Usage    | 1.3.6.1.4.1.2021.11.9.0  | Utilisation CPU en pourcentage    |
| Memory Total | 1.3.6.1.4.1.2021.4.5.0   | Mémoire totale en KB              |
| Memory Used  | 1.3.6.1.4.1.2021.4.6.0   | Mémoire utilisée en KB            |
| Disk Usage   | 1.3.6.1.4.1.2021.9.1.9.1 | Utilisation disque en pourcentage |
| Network In   | 1.3.6.1.2.1.2.2.1.10.1   | Octets reçus                      |
| Network Out  | 1.3.6.1.2.1.2.2.1.16.1   | Octets envoyés                    |

## 🔧 Configuration des alertes email

### Gmail

1. Activer l'authentification à 2 facteurs
2. Générer un mot de passe d'application
3. Utiliser ce mot de passe dans la configuration

### Autres fournisseurs

Adapter les paramètres SMTP selon votre fournisseur :

- **Outlook/Hotmail** : smtp-mail.outlook.com:587
- **Yahoo** : smtp.mail.yahoo.com:587
- **Serveur local** : smtp.votre-serveur.com:25

## 📈 Seuils recommandés

| Métrique | Warning | Critical | Description            |
| -------- | ------- | -------- | ---------------------- |
| CPU      | 70%     | 90%      | Utilisation CPU élevée |
| Mémoire  | 80%     | 95%      | Mémoire RAM saturée    |
| Disque   | 85%     | 95%      | Espace disque faible   |
| Réseau   | 1 MB/s  | 5 MB/s   | Trafic réseau élevé    |

## 🐛 Dépannage

### Erreurs SNMP

- Vérifier que SNMP est activé sur la cible
- Contrôler la communauté SNMP
- Vérifier la connectivité réseau
- Tester avec `snmpwalk -v2c -c public <IP> 1.3.6.1.4.1.2021.11.9.0`

### Erreurs email

- Vérifier les paramètres SMTP
- Contrôler les identifiants
- Vérifier les paramètres de sécurité du fournisseur email

### Performance

- Ajuster l'intervalle de monitoring selon les besoins
- Réduire le timeout SNMP si nécessaire
- Surveiller l'utilisation CPU du script de monitoring

## 📁 Structure des fichiers

```
Script de monitoring réseau ou CPU/
├── monitoring_system.py      # Script principal de monitoring
├── monitoring_ui.py          # Interface graphique
├── start_monitoring.py       # Script de démarrage
├── config.json              # Configuration
├── requirements.txt          # Dépendances Python
├── README.md                # Documentation
├── monitoring.log           # Fichier de logs (créé automatiquement)
└── *.csv                    # Rapports exportés
```

## 🔒 Sécurité

- Utiliser des communautés SNMP sécurisées en production
- Limiter l'accès SNMP aux systèmes de monitoring uniquement
- Utiliser SNMPv3 pour plus de sécurité
- Protéger les mots de passe email
- Surveiller les logs pour détecter les accès non autorisés

## 📝 Logs

Les logs sont enregistrés dans `monitoring.log` avec les niveaux :

- **INFO** : Métriques normales
- **WARNING** : Seuils dépassés
- **ERROR** : Erreurs de connexion ou configuration

## 🤝 Contribution

Pour contribuer au projet :

1. Fork le repository
2. Créer une branche pour votre fonctionnalité
3. Tester vos modifications
4. Soumettre une pull request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🆘 Support

En cas de problème :

1. Consulter la section dépannage
2. Vérifier les logs dans `monitoring.log`
3. Tester la connectivité SNMP manuellement
4. Ouvrir une issue sur le repository

---

**Impact :** Ce système de monitoring permet une **détection proactive** des problèmes système, une **surveillance continue** des ressources et une **alerte précoce** en cas d'anomalies, contribuant à maintenir la stabilité et les performances des infrastructures.
