#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Test SNMP
==================
Teste la connectivité SNMP et récupère les métriques de base
"""

import sys
import time
from pysnmp.hlapi import *
def test_multiple_targets(targets):
    """Teste plusieurs cibles"""
    print("🚀 Test de connectivité SNMP multiple")
    print("=" * 60)
    
    results = {}
    
    for target in targets:
        print(f"\n🎯 Test de {target['name']} ({target['ip']})")
        success = test_snmp_connection(
            target['ip'], 
            community=target.get('community', 'public'),
            port=target.get('port', 161)
        )
        results[target['name']] = success
    
    print("\n" + "=" * 60)
    print("📋 Résumé des tests:")
    
    for name, success in results.items():
        status = "✅ OK" if success else "❌ ÉCHEC"
        print(f"   {name}: {status}")
    
    return results

def interactive_test():
    """Test interactif"""
    print("🔧 Test SNMP Interactif")
    print("=" * 30)
    
    ip = input("Adresse IP de la cible: ").strip()
    if not ip:
        print("❌ Adresse IP requise")
        return
    
    community = input("Community SNMP (défaut: public): ").strip() or "public"
    port = input("Port SNMP (défaut: 161): ").strip() or "161"
    
    try:
        port = int(port)
    except ValueError:
        print("❌ Port invalide")
        return
    
    test_snmp_connection(ip, community, port)

def main():
    """Fonction principale"""
    print("🔍 Script de Test SNMP")
    print("=====================")
    
    if len(sys.argv) > 1:
        # Mode ligne de commande
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("""
Usage:
  python test_snmp.py                    # Test interactif
  python test_snmp.py <IP>              # Test d'une IP
  python test_snmp.py <IP> <community>  # Test avec communauté spécifique
  python test_snmp.py --config          # Test depuis config.json
            """)
            return
        
        elif sys.argv[1] == "--config":
            # Test depuis la configuration
            try:
                import json
                with open('config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                targets = []
                for target in config['targets']:
                    targets.append({
                        'name': target['name'],
                        'ip': target['ip'],
                        'port': target['port'],
                        'community': config['snmp']['community']
                    })
                
                test_multiple_targets(targets)
                
            except FileNotFoundError:
                print("❌ Fichier config.json non trouvé")
            except Exception as e:
                print(f"❌ Erreur: {str(e)}")
        
        else:
            # Test d'une IP spécifique
            ip = sys.argv[1]
            community = sys.argv[2] if len(sys.argv) > 2 else "public"
            test_snmp_connection(ip, community)
    
    else:
        # Mode interactif
        interactive_test()

if __name__ == "__main__":
    main() 