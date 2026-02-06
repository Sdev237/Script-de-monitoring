#!/bin/bash

# Script de lancement pour Linux/Mac
# Rendre exécutable : chmod +x lancer_monitoring.sh

clear
echo "========================================"
echo "   🚀 Script de Monitoring Système"
echo "========================================"
echo

echo "Choisissez une option :"
echo
echo "1. Interface graphique (recommandée)"
echo "2. Monitoring en ligne de commande"
echo "3. Test SNMP"
echo "4. Démonstration"
echo "5. Installer les dépendances"
echo "6. Quitter"
echo

read -p "Votre choix (1-6) : " choix

case $choix in
    1)
        echo
        echo "🖥️  Lancement de l'interface graphique..."
        python3 monitoring_ui.py
        ;;
    2)
        echo
        echo "📊 Lancement du monitoring en ligne de commande..."
        python3 start_monitoring.py
        ;;
    3)
        echo
        echo "🔍 Lancement du test SNMP..."
        python3 test_snmp.py
        ;;
    4)
        echo
        echo "🎭 Lancement de la démonstration..."
        python3 demo_monitoring.py
        ;;
    5)
        echo
        echo "📦 Installation des dépendances..."
        pip3 install -r requirements.txt
        echo
        echo "✅ Installation terminée !"
        read -p "Appuyez sur Entrée pour continuer..."
        ;;
    6)
        echo
        echo "👋 Au revoir !"
        exit 0
        ;;
    *)
        echo
        echo "❌ Choix invalide !"
        read -p "Appuyez sur Entrée pour continuer..."
        ;;
esac

echo
echo "Appuyez sur Entrée pour fermer..."
read 