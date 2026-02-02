#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Utilisateur pour le Monitoring Système
===============================================
Interface graphique pour configurer et gérer le monitoring
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import threading
import time
from datetime import datetime
import subprocess
import sys
import os
from monitoring_system import SystemMonitor

class MonitoringUI:
    """Interface graphique pour le monitoring système"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Monitoring Système - Interface de Gestion")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        self.monitor = None
        self.monitoring_thread = None
        self.is_monitoring = False
        
        self.setup_ui()
        self.load_config()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration de la grille
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Titre
        title_label = ttk.Label(main_frame, text="🚀 Monitoring Système", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Notebook pour les onglets
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Onglet Configuration
        self.setup_config_tab(notebook)
        
        # Onglet Monitoring
        self.setup_monitoring_tab(notebook)
        
        # Onglet Alertes
        self.setup_alerts_tab(notebook)
        
        # Onglet Rapports
        self.setup_reports_tab(notebook)
        
        # Boutons de contrôle
        self.setup_control_buttons(main_frame)
        
        # Status bar
        self.status_var = tk.StringVar(value="Prêt")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def setup_config_tab(self, notebook):
        """Configure l'onglet de configuration"""
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="Configuration")
        
        # Configuration SNMP
        snmp_frame = ttk.LabelFrame(config_frame, text="Configuration SNMP", padding="10")
        snmp_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(snmp_frame, text="Community:").grid(row=0, column=0, sticky=tk.W)
        self.community_var = tk.StringVar(value="public")
        ttk.Entry(snmp_frame, textvariable=self.community_var).grid(row=0, column=1, padx=(10, 0))
        
        ttk.Label(snmp_frame, text="Timeout (s):").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.timeout_var = tk.StringVar(value="3")
        ttk.Entry(snmp_frame, textvariable=self.timeout_var).grid(row=1, column=1, padx=(10, 0), pady=(10, 0))
        
        # Cibles de monitoring
        targets_frame = ttk.LabelFrame(config_frame, text="Cibles de Monitoring", padding="10")
        targets_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Liste des cibles
        self.targets_tree = ttk.Treeview(targets_frame, columns=('name', 'ip', 'port'), show='headings', height=5)
        self.targets_tree.heading('name', text='Nom')
        self.targets_tree.heading('ip', text='Adresse IP')
        self.targets_tree.heading('port', text='Port')
        self.targets_tree.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Boutons pour les cibles
        ttk.Button(targets_frame, text="Ajouter", command=self.add_target).grid(row=1, column=0, padx=(0, 5))
        ttk.Button(targets_frame, text="Modifier", command=self.edit_target).grid(row=1, column=1, padx=5)
        ttk.Button(targets_frame, text="Supprimer", command=self.remove_target).grid(row=1, column=2, padx=(5, 0))
        
        # Seuils d'alerte
        thresholds_frame = ttk.LabelFrame(config_frame, text="Seuils d'Alerte", padding="10")
        thresholds_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # CPU
        ttk.Label(thresholds_frame, text="CPU Warning (%):").grid(row=0, column=0, sticky=tk.W)
        self.cpu_warning_var = tk.StringVar(value="70")
        ttk.Entry(thresholds_frame, textvariable=self.cpu_warning_var).grid(row=0, column=1, padx=(10, 0))
        
        ttk.Label(thresholds_frame, text="CPU Critical (%):").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.cpu_critical_var = tk.StringVar(value="90")
        ttk.Entry(thresholds_frame, textvariable=self.cpu_critical_var).grid(row=0, column=3, padx=(10, 0))
        
        # Mémoire
        ttk.Label(thresholds_frame, text="Mémoire Warning (%):").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.memory_warning_var = tk.StringVar(value="80")
        ttk.Entry(thresholds_frame, textvariable=self.memory_warning_var).grid(row=1, column=1, padx=(10, 0), pady=(10, 0))
        
        ttk.Label(thresholds_frame, text="Mémoire Critical (%):").grid(row=1, column=2, sticky=tk.W, padx=(20, 0), pady=(10, 0))
        self.memory_critical_var = tk.StringVar(value="95")
        ttk.Entry(thresholds_frame, textvariable=self.memory_critical_var).grid(row=1, column=3, padx=(10, 0), pady=(10, 0))
        
        # Configuration email
        email_frame = ttk.LabelFrame(config_frame, text="Configuration Email", padding="10")
        email_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.email_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(email_frame, text="Activer les alertes email", 
                       variable=self.email_enabled_var).grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        ttk.Label(email_frame, text="Serveur SMTP:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.smtp_server_var = tk.StringVar(value="smtp.gmail.com")
        ttk.Entry(email_frame, textvariable=self.smtp_server_var).grid(row=1, column=1, padx=(10, 0), pady=(10, 0))
        
        ttk.Label(email_frame, text="Port SMTP:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.smtp_port_var = tk.StringVar(value="587")
        ttk.Entry(email_frame, textvariable=self.smtp_port_var).grid(row=2, column=1, padx=(10, 0), pady=(10, 0))
        
        ttk.Label(email_frame, text="Email expéditeur:").grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
        self.sender_email_var = tk.StringVar(value="monitoring@example.com")
        ttk.Entry(email_frame, textvariable=self.sender_email_var).grid(row=3, column=1, padx=(10, 0), pady=(10, 0))
        
        ttk.Label(email_frame, text="Mot de passe:").grid(row=4, column=0, sticky=tk.W, pady=(10, 0))
        self.sender_password_var = tk.StringVar()
        ttk.Entry(email_frame, textvariable=self.sender_password_var, show="*").grid(row=4, column=1, padx=(10, 0), pady=(10, 0))
        
        # Bouton de sauvegarde
        ttk.Button(config_frame, text="Sauvegarder la Configuration", 
                  command=self.save_config).grid(row=4, column=0, pady=(20, 0))
    
    def setup_monitoring_tab(self, notebook):
        """Configure l'onglet de monitoring"""
        monitoring_frame = ttk.Frame(notebook)
        notebook.add(monitoring_frame, text="Monitoring")
        
        # Contrôles de monitoring
        controls_frame = ttk.LabelFrame(monitoring_frame, text="Contrôles", padding="10")
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.start_button = ttk.Button(controls_frame, text="Démarrer le Monitoring", 
                                      command=self.start_monitoring)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(controls_frame, text="Arrêter le Monitoring", 
                                     command=self.stop_monitoring, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        # Métriques en temps réel
        metrics_frame = ttk.LabelFrame(monitoring_frame, text="Métriques en Temps Réel", padding="10")
        metrics_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Zone de texte pour les métriques
        self.metrics_text = tk.Text(metrics_frame, height=15, width=80)
        scrollbar = ttk.Scrollbar(metrics_frame, orient=tk.VERTICAL, command=self.metrics_text.yview)
        self.metrics_text.configure(yscrollcommand=scrollbar.set)
        
        self.metrics_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configuration de la grille
        monitoring_frame.columnconfigure(0, weight=1)
        monitoring_frame.rowconfigure(1, weight=1)
        metrics_frame.columnconfigure(0, weight=1)
        metrics_frame.rowconfigure(0, weight=1)
    
    def setup_alerts_tab(self, notebook):
        """Configure l'onglet des alertes"""
        alerts_frame = ttk.Frame(notebook)
        notebook.add(alerts_frame, text="Alertes")
        
        # Historique des alertes
        alerts_label = ttk.Label(alerts_frame, text="Historique des Alertes (24h)", 
                                font=('Arial', 12, 'bold'))
        alerts_label.grid(row=0, column=0, pady=(0, 10))
        
        # Liste des alertes
        self.alerts_tree = ttk.Treeview(alerts_frame, 
                                       columns=('timestamp', 'target', 'level', 'metric', 'message'), 
                                       show='headings', height=15)
        self.alerts_tree.heading('timestamp', text='Heure')
        self.alerts_tree.heading('target', text='Cible')
        self.alerts_tree.heading('level', text='Niveau')
        self.alerts_tree.heading('metric', text='Métrique')
        self.alerts_tree.heading('message', text='Message')
        
        self.alerts_tree.column('timestamp', width=100)
        self.alerts_tree.column('target', width=120)
        self.alerts_tree.column('level', width=80)
        self.alerts_tree.column('metric', width=80)
        self.alerts_tree.column('message', width=300)
        
        self.alerts_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Boutons
        ttk.Button(alerts_frame, text="Actualiser", command=self.refresh_alerts).grid(row=2, column=0, pady=(0, 10))
        
        # Configuration de la grille
        alerts_frame.columnconfigure(0, weight=1)
        alerts_frame.rowconfigure(1, weight=1)
    
    def setup_reports_tab(self, notebook):
        """Configure l'onglet des rapports"""
        reports_frame = ttk.Frame(notebook)
        notebook.add(reports_frame, text="Rapports")
        
        # Contrôles de rapport
        controls_frame = ttk.LabelFrame(reports_frame, text="Génération de Rapports", padding="10")
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(controls_frame, text="Générer Rapport", command=self.generate_report).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(controls_frame, text="Exporter CSV", command=self.export_csv).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(controls_frame, text="Ouvrir Logs", command=self.open_logs).grid(row=0, column=2)
        
        # Zone de rapport
        report_frame = ttk.LabelFrame(reports_frame, text="Rapport", padding="10")
        report_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.report_text = tk.Text(report_frame, height=20, width=80)
        report_scrollbar = ttk.Scrollbar(report_frame, orient=tk.VERTICAL, command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=report_scrollbar.set)
        
        self.report_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        report_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configuration de la grille
        reports_frame.columnconfigure(0, weight=1)
        reports_frame.rowconfigure(1, weight=1)
        report_frame.columnconfigure(0, weight=1)
        report_frame.rowconfigure(0, weight=1)
    
    def setup_control_buttons(self, main_frame):
        """Configure les boutons de contrôle principaux"""
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="Test SNMP", command=self.test_snmp).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Test Email", command=self.test_email).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="Aide", command=self.show_help).grid(row=0, column=2)
    
    def load_config(self):
        """Charge la configuration depuis le fichier"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Charger les valeurs dans l'interface
            self.community_var.set(config['snmp']['community'])
            self.timeout_var.set(str(config['snmp']['timeout']))
            
            # Charger les cibles
            for target in config['targets']:
                self.targets_tree.insert('', 'end', values=(target['name'], target['ip'], target['port']))
            
            # Charger les seuils
            self.cpu_warning_var.set(str(config['thresholds']['cpu_warning']))
            self.cpu_critical_var.set(str(config['thresholds']['cpu_critical']))
            self.memory_warning_var.set(str(config['thresholds']['memory_warning']))
            self.memory_critical_var.set(str(config['thresholds']['memory_critical']))
            
            # Charger la configuration email
            self.email_enabled_var.set(config['alerts']['email_enabled'])
            self.smtp_server_var.set(config['alerts']['smtp_server'])
            self.smtp_port_var.set(str(config['alerts']['smtp_port']))
            self.sender_email_var.set(config['alerts']['sender_email'])
            
        except FileNotFoundError:
            messagebox.showinfo("Information", "Fichier de configuration non trouvé. Une configuration par défaut sera créée.")
    
    def save_config(self):
        """Sauvegarde la configuration"""
        try:
            config = {
                "snmp": {
                    "community": self.community_var.get(),
                    "timeout": int(self.timeout_var.get()),
                    "retries": 3
                },
                "targets": [],
                "thresholds": {
                    "cpu_warning": int(self.cpu_warning_var.get()),
                    "cpu_critical": int(self.cpu_critical_var.get()),
                    "memory_warning": int(self.memory_warning_var.get()),
                    "memory_critical": int(self.memory_critical_var.get()),
                    "disk_warning": 85,
                    "disk_critical": 95,
                    "network_warning": 1000000
                },
                "alerts": {
                    "email_enabled": self.email_enabled_var.get(),
                    "smtp_server": self.smtp_server_var.get(),
                    "smtp_port": int(self.smtp_port_var.get()),
                    "sender_email": self.sender_email_var.get(),
                    "sender_password": self.sender_password_var.get(),
                    "recipients": ["admin@example.com"]
                },
                "monitoring": {
                    "interval": 60,
                    "log_file": "monitoring.log"
                }
            }
            
            # Ajouter les cibles
            for item in self.targets_tree.get_children():
                values = self.targets_tree.item(item)['values']
                config["targets"].append({
                    "name": values[0],
                    "ip": values[1],
                    "port": int(values[2])
                })
            
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            messagebox.showinfo("Succès", "Configuration sauvegardée avec succès!")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
    
    def add_target(self):
        """Ajoute une nouvelle cible"""
        dialog = TargetDialog(self.root, "Ajouter une cible")
        if dialog.result:
            self.targets_tree.insert('', 'end', values=dialog.result)
    
    def edit_target(self):
        """Modifie une cible sélectionnée"""
        selection = self.targets_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une cible à modifier.")
            return
        
        item = selection[0]
        values = self.targets_tree.item(item)['values']
        dialog = TargetDialog(self.root, "Modifier la cible", values)
        if dialog.result:
            self.targets_tree.item(item, values=dialog.result)
    
    def remove_target(self):
        """Supprime une cible sélectionnée"""
        selection = self.targets_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une cible à supprimer.")
            return
        
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cette cible?"):
            self.targets_tree.delete(selection[0])
    
    def start_monitoring(self):
        """Démarre le monitoring"""
        if self.is_monitoring:
            return
        
        try:
            self.monitor = SystemMonitor()
            self.monitoring_thread = threading.Thread(target=self.monitor.start_monitoring)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            
            self.is_monitoring = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.status_var.set("Monitoring actif")
            
            # Démarrer la mise à jour des métriques
            self.update_metrics()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du démarrage du monitoring: {str(e)}")
    
    def stop_monitoring(self):
        """Arrête le monitoring"""
        if not self.is_monitoring:
            return
        
        try:
            if self.monitor:
                self.monitor.stop_monitoring()
            
            self.is_monitoring = False
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.status_var.set("Monitoring arrêté")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'arrêt du monitoring: {str(e)}")
    
    def update_metrics(self):
        """Met à jour les métriques en temps réel"""
        if self.is_monitoring and self.monitor:
            try:
                # Simuler la récupération de métriques
                current_time = datetime.now().strftime('%H:%M:%S')
                metrics_text = f"[{current_time}] Monitoring actif...\n"
                
                # Ajouter les métriques réelles si disponibles
                if hasattr(self.monitor, 'last_metrics'):
                    for target, metrics in self.monitor.last_metrics.items():
                        metrics_text += f"  {target}: CPU={metrics.get('cpu_usage', 'N/A')}%, "
                        metrics_text += f"Mémoire={metrics.get('memory_percent', 'N/A')}%\n"
                
                self.metrics_text.insert(tk.END, metrics_text)
                self.metrics_text.see(tk.END)
                
                # Limiter le nombre de lignes
                lines = self.metrics_text.get('1.0', tk.END).split('\n')
                if len(lines) > 100:
                    self.metrics_text.delete('1.0', '50.0')
            
            except Exception as e:
                self.metrics_text.insert(tk.END, f"Erreur: {str(e)}\n")
        
        # Programmer la prochaine mise à jour
        if self.is_monitoring:
            self.root.after(5000, self.update_metrics)  # Toutes les 5 secondes
    
    def refresh_alerts(self):
        """Actualise la liste des alertes"""
        if self.monitor:
            alerts = self.monitor.get_alert_history(24)
            
            # Vider la liste
            for item in self.alerts_tree.get_children():
                self.alerts_tree.delete(item)
            
            # Ajouter les alertes
            for alert in alerts:
                self.alerts_tree.insert('', 'end', values=(
                    alert['timestamp'].strftime('%H:%M:%S'),
                    alert['target'],
                    alert['alert']['level'],
                    alert['alert']['metric'],
                    alert['alert']['message']
                ))
    
    def generate_report(self):
        """Génère un rapport"""
        if self.monitor:
            report = self.monitor.generate_report()
            self.report_text.delete('1.0', tk.END)
            self.report_text.insert('1.0', report)
        else:
            self.report_text.delete('1.0', tk.END)
            self.report_text.insert('1.0', "Aucun monitoring actif. Démarrez le monitoring pour générer un rapport.")
    
    def export_csv(self):
        """Exporte les données en CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("Timestamp,Cible,Niveau,Métrique,Valeur,Message\n")
                    if self.monitor:
                        alerts = self.monitor.get_alert_history(24)
                        for alert in alerts:
                            f.write(f"{alert['timestamp']},{alert['target']},{alert['alert']['level']},"
                                   f"{alert['alert']['metric']},{alert['alert']['value']},{alert['alert']['message']}\n")
                
                messagebox.showinfo("Succès", f"Données exportées vers {filename}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")
    
    def open_logs(self):
        """Ouvre le fichier de logs"""
        try:
            if os.path.exists("monitoring.log"):
                if sys.platform == "win32":
                    os.startfile("monitoring.log")
                else:
                    subprocess.run(["xdg-open", "monitoring.log"])
            else:
                messagebox.showinfo("Information", "Aucun fichier de log trouvé.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ouverture du log: {str(e)}")
    
    def test_snmp(self):
        """Teste la connexion SNMP"""
        try:
            # Test simple avec la première cible
            targets = []
            for item in self.targets_tree.get_children():
                values = self.targets_tree.item(item)['values']
                targets.append({
                    "name": values[0],
                    "ip": values[1],
                    "port": int(values[2])
                })
            
            if not targets:
                messagebox.showwarning("Attention", "Aucune cible configurée.")
                return
            
            target = targets[0]
            monitor = SystemMonitor()
            cpu_usage = monitor.get_snmp_value(target, monitor.snmp_oids['cpu_usage'])
            
            if cpu_usage is not None:
                messagebox.showinfo("Test SNMP", f"Connexion SNMP réussie!\nCPU: {cpu_usage:.1f}%")
            else:
                messagebox.showerror("Test SNMP", "Échec de la connexion SNMP.")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du test SNMP: {str(e)}")
    
    def test_email(self):
        """Teste l'envoi d'email"""
        try:
            if not self.email_enabled_var.get():
                messagebox.showinfo("Test Email", "Les alertes email sont désactivées.")
                return
            
            # Test d'envoi d'email
            msg = MIMEMultipart()
            msg['From'] = self.sender_email_var.get()
            msg['To'] = self.sender_email_var.get()  # Envoi à soi-même pour le test
            msg['Subject'] = "Test - Monitoring Système"
            
            body = "Ceci est un email de test du système de monitoring."
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server_var.get(), int(self.smtp_port_var.get()))
            server.starttls()
            server.login(self.sender_email_var.get(), self.sender_password_var.get())
            server.send_message(msg)
            server.quit()
            
            messagebox.showinfo("Test Email", "Email de test envoyé avec succès!")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du test email: {str(e)}")
    
    def show_help(self):
        """Affiche l'aide"""
        help_text = """
        AIDE - Monitoring Système
        =========================
        
        Configuration:
        - Configurez les cibles SNMP à surveiller
        - Définissez les seuils d'alerte
        - Configurez les alertes email
        
        Monitoring:
        - Démarrez le monitoring pour surveiller les systèmes
        - Consultez les métriques en temps réel
        - Surveillez les alertes générées
        
        Rapports:
        - Générez des rapports de monitoring
        - Exportez les données en CSV
        - Consultez les logs
        
        Prérequis:
        - SNMP activé sur les systèmes cibles
        - Configuration email valide pour les alertes
        - Bibliothèques Python: pysnmp, tkinter
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Aide")
        help_window.geometry("500x400")
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.insert('1.0', help_text)
        text_widget.config(state='disabled')
        
        scrollbar = ttk.Scrollbar(help_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

class TargetDialog:
    """Dialogue pour ajouter/modifier une cible"""
    
    def __init__(self, parent, title, values=None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Variables
        self.name_var = tk.StringVar(value=values[0] if values else "")
        self.ip_var = tk.StringVar(value=values[1] if values else "")
        self.port_var = tk.StringVar(value=str(values[2]) if values else "161")
        
        # Interface
        ttk.Label(self.dialog, text="Nom:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Entry(self.dialog, textvariable=self.name_var).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(self.dialog, text="IP:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Entry(self.dialog, textvariable=self.ip_var).grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(self.dialog, text="Port:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Entry(self.dialog, textvariable=self.port_var).grid(row=2, column=1, padx=10, pady=5)
        
        # Boutons
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="OK", command=self.ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Annuler", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # Focus sur le premier champ
        self.dialog.focus_set()
        self.dialog.wait_window()
    
    def ok(self):
        """Valide la saisie"""
        if self.name_var.get() and self.ip_var.get():
            try:
                port = int(self.port_var.get())
                self.result = (self.name_var.get(), self.ip_var.get(), port)
                self.dialog.destroy()
            except ValueError:
                messagebox.showerror("Erreur", "Le port doit être un nombre entier.")
        else:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
    
    def cancel(self):
        """Annule la saisie"""
        self.dialog.destroy()

def main():
    """Fonction principale"""
    root = tk.Tk()
    app = MonitoringUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 