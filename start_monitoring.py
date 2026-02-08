#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Démarrage - Monitoring Système
=======================================
Script simple pour démarrer le monitoring en ligne de commande
"""

import sys
import os
from monitoring_system import SystemMonitor

def main():
    """Démarre le monitoring en mode console"""
    print("🚀 Démarrage du Monitoring Système")
    print("==================================")
    
    try:
        # Vérifier si le fichier de configuration existe
        if not os.path.exists('config.json'):
            print("⚠️  Fichier config.json non trouvé. Utilisation de la configuration par défaut.")
        
        # Créer l'instance de monitoring
        monitor = SystemMonitor()
        
        print(f"✅ Configuration chargée:")
        print(f"   - Cibles: {len(monitor.config['targets'])}")
        print(f"   - Intervalle: {monitor.config['monitoring']['interval']}s")
        print(f"   - Log: {monitor.config['monitoring']['log_file']}")
        
        print("\n📊 Démarrage du monitoring...")
        print("Appuyez sur Ctrl+C pour arrêter\n")
        
        # Démarrer le monitoring
        monitor.start_monitoring()
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur")
        if 'monitor' in locals():
            monitor.stop_monitoring()
        print("✅ Monitoring arrêté proprement")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        print("\n💡 Vérifiez:")
        print("   - La configuration SNMP")
        print("   - La connectivité réseau")
        print("   - Les permissions d'accès")
        sys.exit(1)

if __name__ == "__main__":
    main() 