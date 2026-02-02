
"""
Script de Démonstration - Monitoring Système
===========================================
Simule des métriques SNMP pour tester le système de monitoring
"""

import time
import random
import threading
from datetime import datetime
import json
import os

class SNMPSimulator:
    """Simulateur SNMP pour les tests"""
    
    def __init__(self, config_file="demo_config.json"):
        self.config = self.load_demo_config(config_file)
        self.running = False
        self.metrics = {}
        
    def load_demo_config(self, config_file):
        """Charge la configuration de démonstration"""
        demo_config = {
            "targets": [
                {
                    "name": "Serveur Demo 1",
                    "ip": "192.168.1.200",
                    "port": 161
                },
                {
                    "name": "Serveur Demo 2", 
                    "ip": "192.168.1.201",
                    "port": 161
                }
            ],
            "simulation": {
                "interval": 30,  # secondes
                "cpu_base": 30,  # % de base
                "memory_base": 50,  # % de base
                "disk_base": 60,  # % de base
                "network_base": 100000  # octets de base
            },
            "anomalies": {
                "enabled": True,
                "probability": 0.1,  # 10% de chance d'anomalie
                "duration": 300  # durée en secondes
            }
        }
        
        # Sauvegarder la configuration de démonstration
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(demo_config, f, indent=4, ensure_ascii=False)
        
        return demo_config
    
    def generate_metrics(self, target):
        """Génère des métriques simulées pour une cible"""
        base_config = self.config["simulation"]
        anomaly_config = self.config["anomalies"]
        
        # Vérifier si une anomalie doit être générée
        if anomaly_config["enabled"] and random.random() < anomaly_config["probability"]:
            # Générer une anomalie
            anomaly_type = random.choice(["cpu_spike", "memory_spike", "disk_spike", "network_spike"])
            
            if anomaly_type == "cpu_spike":
                cpu_usage = min(100, base_config["cpu_base"] + random.randint(40, 60))
                memory_usage = base_config["memory_base"] + random.randint(-10, 10)
                disk_usage = base_config["disk_base"] + random.randint(-5, 5)
                network_usage = base_config["network_base"] + random.randint(-20000, 20000)
                
            elif anomaly_type == "memory_spike":
                cpu_usage = base_config["cpu_base"] + random.randint(-10, 10)
                memory_usage = min(100, base_config["memory_base"] + random.randint(30, 50))
                disk_usage = base_config["disk_base"] + random.randint(-5, 5)
                network_usage = base_config["network_base"] + random.randint(-20000, 20000)
                
            elif anomaly_type == "disk_spike":
                cpu_usage = base_config["cpu_base"] + random.randint(-10, 10)
                memory_usage = base_config["memory_base"] + random.randint(-10, 10)
                disk_usage = min(100, base_config["disk_base"] + random.randint(25, 35))
                network_usage = base_config["network_base"] + random.randint(-20000, 20000)
                
            else:  # network_spike
                cpu_usage = base_config["cpu_base"] + random.randint(-10, 10)
                memory_usage = base_config["memory_base"] + random.randint(-10, 10)
                disk_usage = base_config["disk_base"] + random.randint(-5, 5)
                network_usage = base_config["network_base"] + random.randint(500000, 1000000)
                
            print(f"🚨 ANOMALIE détectée sur {target['name']}: {anomaly_type}")
            
        else:
            # Métriques normales avec variation
            cpu_usage = max(0, min(100, base_config["cpu_base"] + random.randint(-15, 15)))
            memory_usage = max(0, min(100, base_config["memory_base"] + random.randint(-10, 10)))
            disk_usage = max(0, min(100, base_config["disk_base"] + random.randint(-5, 5)))
            network_usage = max(0, base_config["network_base"] + random.randint(-50000, 50000))
        
        return {
            'timestamp': datetime.now().isoformat(),
            'target': target['name'],
            'ip': target['ip'],
            'cpu_usage': cpu_usage,
            'memory_total': 8192,  # 8 GB
            'memory_used': int(8192 * memory_usage / 100),
            'memory_percent': memory_usage,
            'disk_usage': disk_usage,
            'network_in': network_usage // 2,
            'network_out': network_usage // 2,
            'network_total': network_usage
        }
    
    def start_simulation(self):
        """Démarre la simulation"""
        self.running = True
        print("🎭 Démarrage de la simulation SNMP")
        print("=" * 50)
        
        while self.running:
            for target in self.config["targets"]:
                metrics = self.generate_metrics(target)
                self.metrics[target['name']] = metrics
                
                # Afficher les métriques
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {target['name']}: "
                      f"CPU={metrics['cpu_usage']:.1f}%, "
                      f"Mémoire={metrics['memory_percent']:.1f}%, "
                      f"Disque={metrics['disk_usage']:.1f}%")
            
            time.sleep(self.config["simulation"]["interval"])
    
    def stop_simulation(self):
        """Arrête la simulation"""
        self.running = False
        print("🛑 Simulation arrêtée")
    
    def get_metrics(self, target_name):
        """Récupère les métriques d'une cible"""
        return self.metrics.get(target_name, {})

def create_demo_config():
    """Crée une configuration de démonstration pour le monitoring"""
    demo_config = {
        "snmp": {
            "community": "public",
            "timeout": 3,
            "retries": 3
        },
        "targets": [
            {
                "name": "Serveur Demo 1",
                "ip": "192.168.1.200",
                "port": 161
            },
            {
                "name": "Serveur Demo 2",
                "ip": "192.168.1.201", 
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
            "email_enabled": False,  # Désactivé pour la démo
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "demo@example.com",
            "sender_password": "",
            "recipients": ["admin@example.com"]
        },
        "monitoring": {
            "interval": 30,  # Plus rapide pour la démo
            "log_file": "demo_monitoring.log"
        }
    }
    
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(demo_config, f, indent=4, ensure_ascii=False)
    
    print("✅ Configuration de démonstration créée (config.json)")

def main():
    """Fonction principale de démonstration"""
    print("🎭 Script de Démonstration - Monitoring Système")
    print("=" * 60)
    
    # Créer la configuration de démonstration
    create_demo_config()
    
    # Démarrer le simulateur
    simulator = SNMPSimulator()
    
    try:
        # Démarrer la simulation dans un thread
        sim_thread = threading.Thread(target=simulator.start_simulation)
        sim_thread.daemon = True
        sim_thread.start()
        
        print("\n📊 Simulation en cours...")
        print("💡 Vous pouvez maintenant:")
        print("   - Lancer le monitoring: python monitoring_system.py")
        print("   - Ouvrir l'interface: python monitoring_ui.py")
        print("   - Appuyer sur Ctrl+C pour arrêter la simulation")
        
        # Attendre l'interruption
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt de la démonstration...")
        simulator.stop_simulation()
        print("✅ Démonstration terminée")

if __name__ == "__main__":
    main() 