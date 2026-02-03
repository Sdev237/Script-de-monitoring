@echo off
chcp 65001 >nul
title Monitoring Système

echo.
echo ========================================
echo    Script de Monitoring Système
echo ========================================
echo.

echo Choisissez une option :
echo.
echo 1. Interface graphique (recommandée)
echo 2. Monitoring en ligne de commande
echo 3. Test SNMP
echo 4. Démonstration
echo 5. Installer les dépendances
echo 6. Quitter
echo.

set /p choix="Votre choix (1-6) : "

if "%choix%"=="1" (
    echo.
    echo 🖥️  Lancement de l'interface graphique...
    python monitoring_ui.py
    goto :fin
)

if "%choix%"=="2" (
    echo.
    echo 📊 Lancement du monitoring en ligne de commande...
    python start_monitoring.py
    goto :fin
)

if "%choix%"=="3" (
    echo.
    echo 🔍 Lancement du test SNMP...
    python test_snmp.py
    goto :fin
)


if "%choix%"=="6" (
    echo.
    echo 👋 Au revoir !
    goto :fin
)

echo.
echo ❌ Choix invalide !
pause

:fin
echo.
echo Appuyez sur une touche pour fermer...
pause >nul 