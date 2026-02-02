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

def test_snmp_connection(ip, community="public", port=161, timeout=3):
    """Teste la connexion SNMP vers une cible"""
    print(f"🔍 Test de connexion SNMP vers {ip}:{port}")
    print("=" * 50)
    
    # OIDs de test
    test_oids = {
        'System Description': '1.3.6.1.2.1.1.1.0',
        'System Uptime': '1.3.6.1.2.1.1.3.0',
        'CPU Usage': '1.3.6.1.4.1.2021.11.9.0',
        'Memory Total': '1.3.6.1.4.1.2021.4.5.0',
        'Memory Used': '1.3.6.1.4.1.2021.4.6.0',
        'Disk Usage': '1.3.6.1.4.1.2021.9.1.9.1',
        'Network In': '1.3.6.1.2.1.2.2.1.10.1',
        'Network Out': '1.3.6.1.2.1.2.2.1.16.1'
    }
    
    success_count = 0
    total_count = len(test_oids)
    
    for name, oid in test_oids.items():
        try:
            print(f"📡 Test de {name} ({oid})...", end=" ")
            
            iterator = getCmd(
                SnmpEngine(),
                CommunityData(community),
                UdpTransportTarget((ip, port), timeout=timeout, retries=1),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
            
            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
            
            if errorIndication:
                print(f"❌ Erreur: {errorIndication}")
            elif errorStatus:
                print(f"❌ Erreur: {errorStatus}")
            else:
                for varBind in varBinds:
                    value = varBind[1]
                    if name == 'System Description':
                        print(f"✅ {value}")
                    elif name == 'System Uptime':
                        uptime_seconds = int(value)
                        uptime_hours = uptime_seconds // 3600
                        uptime_days = uptime_hours // 24
                        print(f"✅ {uptime_days} jours, {uptime_hours % 24} heures")
                    elif name in ['CPU Usage', 'Disk Usage']:
                        print(f"✅ {value}%")
                    elif name in ['Memory Total', 'Memory Used']:
                        memory_mb = int(value) // 1024
                        print(f"✅ {memory_mb} MB")
                    elif name in ['Network In', 'Network Out']:
                        print(f"✅ {value} octets")
                    else:
                        print(f"✅ {value}")
                success_count += 1
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 Résultats: {success_count}/{total_count} OIDs accessibles")
    
    if success_count == 0:
        print("❌ Aucune connexion SNMP possible")
        print("\n💡 Vérifiez:")
        print("   - SNMP est-il activé sur la cible?")
        print("   - La communauté SNMP est-elle correcte?")
        print("   - Le port 161/UDP est-il ouvert?")
        print("   - La connectivité réseau est-elle OK?")
        return False
    elif success_count < total_count:
        print("⚠️  Connexion partielle - certains OIDs ne sont pas disponibles")
        print("   Cela peut être normal selon le système d'exploitation")
        return True
    else:
        print("✅ Connexion SNMP complète!")
        return True

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