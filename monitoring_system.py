#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Monitoring Réseau et CPU
==================================
Surveillance des ressources système avec SNMP et alertes en cas de dépassement
"""

import time
import logging
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import threading
from typing import Dict, List, Optional
import pysnmp
from pysnmp.hlapi import *

class SystemMonitor:
    """Classe principale pour le monitoring système via SNMP"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.alert_history = []
        self.monitoring_active = False
        
        # OIDs SNMP pour les métriques système
        self.snmp_oids = {
            'cpu_usage': '1.3.6.1.4.1.2021.11.9.0',  # CPU usage
            'memory_total': '1.3.6.1.4.1.2021.4.5.0',  # Total RAM
            'memory_used': '1.3.6.1.4.1.2021.4.6.0',   # Used RAM
            'network_in': '1.3.6.1.2.1.2.2.1.10.1',   # Octets in
            'network_out': '1.3.6.1.2.1.2.2.1.16.1',  # Octets out
            'disk_usage': '1.3.6.1.4.1.2021.9.1.9.1'  # Disk usage
        }
        
    def load_config(self, config_file: str) -> Dict:
        """Charge la configuration depuis un fichier JSON"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Configuration par défaut
            default_config = {
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
                    "network_warning": 1000000  # 1 MB/s
                },
                "alerts": {
                    "email_enabled": True,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "sender_email": "monitoring@example.com",
                    "sender_password": "",
                    "recipients": ["admin@example.com"]
                },
                "monitoring": {
                    "interval": 60,  # secondes
                    "log_file": "monitoring.log"
                }
            }
            # Sauvegarder la configuration par défaut
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            return default_config
    
    def setup_logging(self):
        """Configure le système de logging"""
        log_file = self.config["monitoring"]["log_file"]
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_snmp_value(self, target: Dict, oid: str) -> Optional[float]:
        """Récupère une valeur via SNMP"""
        try:
            iterator = getCmd(
                SnmpEngine(),
                CommunityData(self.config["snmp"]["community"]),
                UdpTransportTarget((target["ip"], target["port"]), 
                                 timeout=self.config["snmp"]["timeout"],
                                 retries=self.config["snmp"]["retries"]),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
            
            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
            
            if errorIndication:
                self.logger.error(f"Erreur SNMP pour {target['name']}: {errorIndication}")
                return None
            elif errorStatus:
                self.logger.error(f"Erreur SNMP pour {target['name']}: {errorStatus}")
                return None
            else:
                for varBind in varBinds:
                    return float(varBind[1])
                    
        except Exception as e:
            self.logger.error(f"Exception SNMP pour {target['name']}: {str(e)}")
            return None
    
    def get_system_metrics(self, target: Dict) -> Dict:
        """Récupère toutes les métriques système pour une cible"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'target': target['name'],
            'ip': target['ip']
        }
        
        # CPU Usage
        cpu_usage = self.get_snmp_value(target, self.snmp_oids['cpu_usage'])
        if cpu_usage is not None:
            metrics['cpu_usage'] = cpu_usage
        
        # Memory
        memory_total = self.get_snmp_value(target, self.snmp_oids['memory_total'])
        memory_used = self.get_snmp_value(target, self.snmp_oids['memory_used'])
        if memory_total and memory_used:
            memory_percent = (memory_used / memory_total) * 100
            metrics['memory_total'] = memory_total
            metrics['memory_used'] = memory_used
            metrics['memory_percent'] = memory_percent
        
    
        
        return metrics
    
    def check_thresholds(self, metrics: Dict) -> List[Dict]:
        """Vérifie les seuils et génère des alertes"""
        alerts = []
        thresholds = self.config["thresholds"]
        
        # Vérification CPU
        if 'cpu_usage' in metrics:
            cpu_usage = metrics['cpu_usage']
            if cpu_usage >= thresholds['cpu_critical']:
                alerts.append({
                    'level': 'CRITICAL',
                    'metric': 'CPU',
                    'value': cpu_usage,
                    'threshold': thresholds['cpu_critical'],
                    'message': f"CPU critique: {cpu_usage:.1f}% (seuil: {thresholds['cpu_critical']}%)"
                })
            elif cpu_usage >= thresholds['cpu_warning']:
                alerts.append({
                    'level': 'WARNING',
                    'metric': 'CPU',
                    'value': cpu_usage,
                    'threshold': thresholds['cpu_warning'],
                    'message': f"CPU élevé: {cpu_usage:.1f}% (seuil: {thresholds['cpu_warning']}%)"
                })
        
        # Vérification Mémoire
        if 'memory_percent' in metrics:
            memory_percent = metrics['memory_percent']
            if memory_percent >= thresholds['memory_critical']:
                alerts.append({
                    'level': 'CRITICAL',
                    'metric': 'Mémoire',
                    'value': memory_percent,
                    'threshold': thresholds['memory_critical'],
                    'message': f"Mémoire critique: {memory_percent:.1f}% (seuil: {thresholds['memory_critical']}%)"
                })
            elif memory_percent >= thresholds['memory_warning']:
                alerts.append({
                    'level': 'WARNING',
                    'metric': 'Mémoire',
                    'value': memory_percent,
                    'threshold': thresholds['memory_warning'],
                    'message': f"Mémoire élevée: {memory_percent:.1f}% (seuil: {thresholds['memory_warning']}%)"
                })
        
        # Vérification Disque
        if 'disk_usage' in metrics:
            disk_usage = metrics['disk_usage']
            if disk_usage >= thresholds['disk_critical']:
                alerts.append({
                    'level': 'CRITICAL',
                    'metric': 'Disque',
                    'value': disk_usage,
                    'threshold': thresholds['disk_critical'],
                    'message': f"Disque critique: {disk_usage:.1f}% (seuil: {thresholds['disk_critical']}%)"
                })
            elif disk_usage >= thresholds['disk_warning']:
                alerts.append({
                    'level': 'WARNING',
                    'metric': 'Disque',
                    'value': disk_usage,
                    'threshold': thresholds['disk_warning'],
                    'message': f"Disque élevé: {disk_usage:.1f}% (seuil: {thresholds['disk_warning']}%)"
                })
        
        return alerts
    
    def send_email_alert(self, alert: Dict, metrics: Dict):
        """Envoie une alerte par email"""
        if not self.config["alerts"]["email_enabled"]:
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config["alerts"]["sender_email"]
            msg['To'] = ", ".join(self.config["alerts"]["recipients"])
            msg['Subject'] = f"ALERTE {alert['level']} - {metrics['target']}"
            
            body = f"""
            <html>
            <body>
                <h2>🚨 Alerte de Monitoring Système</h2>
                <p><strong>Serveur:</strong> {metrics['target']} ({metrics['ip']})</p>
                <p><strong>Niveau:</strong> {alert['level']}</p>
                <p><strong>Métrique:</strong> {alert['metric']}</p>
                <p><strong>Valeur:</strong> {alert['value']:.1f}</p>
                <p><strong>Seuil:</strong> {alert['threshold']}</p>
                <p><strong>Message:</strong> {alert['message']}</p>
                <p><strong>Timestamp:</strong> {metrics['timestamp']}</p>
                
                <h3>Métriques actuelles:</h3>
                <ul>
            """
            
            for key, value in metrics.items():
                if key not in ['timestamp', 'target', 'ip']:
                    if isinstance(value, float):
                        body += f"<li><strong>{key}:</strong> {value:.1f}</li>"
                    else:
                        body += f"<li><strong>{key}:</strong> {value}</li>"
            
            body += """
                </ul>
                <p><em>Cet email a été généré automatiquement par le système de monitoring.</em></p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.config["alerts"]["smtp_server"], 
                                self.config["alerts"]["smtp_port"])
            server.starttls()
            server.login(self.config["alerts"]["sender_email"], 
                        self.config["alerts"]["sender_password"])
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email d'alerte envoyé pour {metrics['target']}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
    
    def log_metrics(self, metrics: Dict):
        """Enregistre les métriques dans le log"""
        self.logger.info(f"Métriques pour {metrics['target']}: "
                        f"CPU: {metrics.get('cpu_usage', 'N/A'):.1f}%, "
                        f"Mémoire: {metrics.get('memory_percent', 'N/A'):.1f}%, "
                        f"Disque: {metrics.get('disk_usage', 'N/A'):.1f}%")
    
    def monitor_target(self, target: Dict):
        """Surveille une cible spécifique"""
        try:
            metrics = self.get_system_metrics(target)
            if metrics:
                self.log_metrics(metrics)
                alerts = self.check_thresholds(metrics)
                
                for alert in alerts:
                    self.alert_history.append({
                        'timestamp': datetime.now(),
                        'target': target['name'],
                        'alert': alert,
                        'metrics': metrics
                    })
                    
                    self.logger.warning(f"ALERTE {alert['level']} - {alert['message']}")
                    self.send_email_alert(alert, metrics)
                    
        except Exception as e:
            self.logger.error(f"Erreur lors du monitoring de {target['name']}: {str(e)}")
    
    def start_monitoring(self):
        """Démarre le monitoring continu"""
        self.monitoring_active = True
        self.logger.info("Démarrage du monitoring système...")
        
        while self.monitoring_active:
            for target in self.config["targets"]:
                self.monitor_target(target)
            
            # Attendre l'intervalle configuré
            time.sleep(self.config["monitoring"]["interval"])
    
    def stop_monitoring(self):
        """Arrête le monitoring"""
        self.monitoring_active = False
        self.logger.info("Arrêt du monitoring système")
    
    def get_alert_history(self, hours: int = 24) -> List[Dict]:
        """Récupère l'historique des alertes des dernières heures"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alert_history if alert['timestamp'] > cutoff_time]
    
    def generate_report(self) -> str:
        """Génère un rapport de monitoring"""
        recent_alerts = self.get_alert_history(24)
        
        report = f"""
        ========================================
        RAPPORT DE MONITORING SYSTÈME
        ========================================
        Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        CIBLES SURVEILLÉES:
        """
        
        for target in self.config["targets"]:
            report += f"- {target['name']} ({target['ip']})\n"
        
        report += f"""
        
        ALERTES (24h):
        Total: {len(recent_alerts)}
        """
        
        critical_count = len([a for a in recent_alerts if a['alert']['level'] == 'CRITICAL'])
        warning_count = len([a for a in recent_alerts if a['alert']['level'] == 'WARNING'])
        
        report += f"Critiques: {critical_count}\n"
        report += f"Avertissements: {warning_count}\n"
        
        if recent_alerts:
            report += "\nDERNIÈRES ALERTES:\n"
            for alert in recent_alerts[-5:]:  # 5 dernières alertes
                report += f"- {alert['timestamp'].strftime('%H:%M:%S')} - {alert['target']}: {alert['alert']['message']}\n"
        
        return report

def main():
    """Fonction principale"""
    print("🚀 Script de Monitoring Réseau et CPU")
    print("=====================================")
    
    try:
        monitor = SystemMonitor()
        
        # Démarrer le monitoring dans un thread séparé
        monitoring_thread = threading.Thread(target=monitor.start_monitoring)
        monitoring_thread.daemon = True
        monitoring_thread.start()
        
        print("✅ Monitoring démarré. Appuyez sur Ctrl+C pour arrêter.")
        print("📊 Génération de rapports toutes les 5 minutes...")
        
        # Boucle principale pour générer des rapports
        while True:
            time.sleep(300)  # 5 minutes
            report = monitor.generate_report()
            print("\n" + report)
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du monitoring...")
        monitor.stop_monitoring()
        print("✅ Monitoring arrêté.")
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")

if __name__ == "__main__":
    main() 