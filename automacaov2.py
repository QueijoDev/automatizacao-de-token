import customtkinter as ctk
from tkinter import messagebox
import threading
import time
import PyKCS11
from PyKCS11 import *
import sys
import ctypes
import winreg
import os

# --- TENTATIVA DE IMPORTAR DADOS REAIS ---
try:
    from segredos import PUK_REAL, PIN_REAL, LABEL_REAL
    
    # Se encontrou o arquivo, usa os dados reais
    PUK_FINAL = PUK_REAL
    PIN_FINAL = PIN_REAL
    LABEL_VISUAL = LABEL_REAL
    MODO_SEGURO = False 

except ImportError:
    # Se baixou do GitHub (sem segredos.py), usa dados genéricos
    PUK_FINAL = "SENHA_ADMIN"
    PIN_FINAL = "SENHA_USER"
    LABEL_VISUAL = "NOME_DO_TOKEN"
    MODO_SEGURO = True

# --- CONFIGURAÇÕES TÉCNICAS ---
DLL_PATH = r"C:\Windows\System32\aetpkss1.dll"
# Garante que o Label tenha sempre 32 caracteres (exigência do driver)
LABEL_FINAL = LABEL_VISUAL.ljust(32, ' ')

# --- CONFIGURAÇÕES VISUAIS ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da Janela
        self.title(f"Configurador | {LABEL_VISUAL}")
        self.geometry("600x550")
        self.resizable(False, False)
        
        # Variáveis de Controle
        self.pkcs11 = None
        self.lista_slots = []
        self.processando = False

        # --- LAYOUT ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Cabeçalho
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(20, 10))
        
        # TÍTULO DINÂMICO (Pega o nome do segredos.py)
        self.lbl_titulo = ctk.CTkLabel(self.header_frame, text=LABEL_VISUAL.upper(), 
                                     font=ctk.CTkFont(size=26, weight="bold"))
        self.lbl_titulo.pack()
        
        self.lbl_subtitulo = ctk.CTkLabel(self.header_frame, text="Sistema de Inicialização de Token", 
                                        text_color="gray", font=ctk.CTkFont(size=14))
        self.lbl_subtitulo.pack()

        # 2. Área Central
        self.status_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=("#EBEBEB", "#2B2B2B"))
        self.status_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        
        # Ícone Principal
        self.lbl_icon = ctk.CTkLabel(self.status_frame, text="🛡️", font=ctk.CTkFont(size=100))
        self.lbl_icon.place(relx=0.5, rely=0.35, anchor="center")
        
        self.lbl_status_main = ctk.CTkLabel(self.status_frame, text="Iniciando...", 
                                          font=ctk.CTkFont(size=22, weight="bold"))
        self.lbl_status_main.place(relx=0.5, rely=0.60, anchor="center")
        
        self.lbl_detalhes = ctk.CTkLabel(self.status_frame, text="", font=ctk.CTkFont(size=14))
        self.lbl_detalhes.place(relx=0.5, rely=0.80, anchor="center")

        # Barra de Progresso
        self.progressbar = ctk.CTkProgressBar(self.status_frame, width=350, height=15, mode="indeterminate")

        # 3. Rodapé
        self.footer_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.footer_frame.grid(row=2, column=0, sticky="ew", pady=30, padx=40)
        
        self.btn_acao = ctk.CTkButton(self.footer_frame, 
                                    text="AGUARDANDO...", 
                                    font=ctk.CTkFont(size=16, weight="bold"),
                                    height=55,
                                    fg_color="#1F6AA5",
                                    state="disabled",
                                    command=self.iniciar_lote)
        self.btn_acao.pack(fill="x")

        # Aviso de Modo Seguro (Sem senhas)
        if MODO_SEGURO:
            self.lbl_subtitulo.configure(text="MODO DEMONSTRAÇÃO (Dados Genéricos)", text_color="orange")

        self.after(100, self.garantir_ambiente)

    # --- SISTEMA ---
    def is_admin(self):
        try: return ctypes.windll.shell32.IsUserAnAdmin()
        except: return False

    def garantir_ambiente(self):
        if not self.is_admin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
        else:
            self.aplicar_correcao_registro()
            threading.Thread(target=self.monitorar_slots, daemon=True).start()

    def aplicar_correcao_registro(self):
        caminhos = [
            r"SOFTWARE\A.E.T. Europe B.V.\SafeSign\2.0\TokenAdministration",
            r"SOFTWARE\WOW6432Node\A.E.T. Europe B.V.\SafeSign\2.0\TokenAdministration"
        ]
        for caminho in caminhos:
            try:
                key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, caminho)
                winreg.SetValueEx(key, "EnableInitToken", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(key)
            except: pass

    # --- MONITORAMENTO ---
    def carregar_driver(self):
        try:
            lib = PyKCS11.PyKCS11Lib()
            lib.load(DLL_PATH)
            return lib
        except: return None

    def monitorar_slots(self):
        self.pkcs11 = self.carregar_driver()
        if not self.pkcs11:
            self.atualizar_ui_erro("Driver SafeSign ausente.")
            return

        while True:
            if not self.processando:
                try:
                    slots = self.pkcs11.getSlotList(tokenPresent=True)
                    self.lista_slots = slots
                    
                    if not slots:
                        self.atualizar_ui_aguardando()
                    else:
                        self.analisar_tokens(slots)
                except Exception:
                    pass
            time.sleep(1.5)

    def analisar_tokens(self, slots):
        detalhes = ""
        pendentes = False
        prontos = 0
        
        for i, slot in enumerate(slots):
            try:
                info = self.pkcs11.getTokenInfo(slot)
                label = info.label
                # Verifica se o nome do token bate com o nome configurado
                if label.startswith(LABEL_VISUAL):
                    detalhes += f"Token {i+1}: ✅ Configurado\n"
                    prontos += 1
                else:
                    detalhes += f"Token {i+1}: ⚠️ CONFIGURAR AGORA\n"
                    pendentes = True
            except:
                detalhes += f"Token {i+1}: ❌ Erro\n"

        if pendentes:
            self.atualizar_ui_pendente(detalhes)
        elif prontos > 0:
            self.atualizar_ui_pronto(detalhes)

    # --- ATUALIZAÇÕES VISUAIS ---
    def atualizar_ui_aguardando(self):
        self.lbl_icon.configure(text="🛡️", text_color="gray")
        self.lbl_status_main.configure(text="Aguardando Conexão...", text_color="gray")
        self.lbl_detalhes.configure(text="Insira o Token USB")
        self.status_frame.configure(border_color="gray", border_width=0)
        self.btn_acao.configure(state="disabled", text="AGUARDANDO...", fg_color="#333333")

    def atualizar_ui_pendente(self, txt):
        self.lbl_icon.configure(text="🔑", text_color="#FF9800")
        self.lbl_status_main.configure(text="Token Detectado", text_color="#FF9800")
        self.lbl_detalhes.configure(text=txt)
        self.status_frame.configure(border_color="#FF9800", border_width=2)
        
        if MODO_SEGURO:
             self.btn_acao.configure(state="disabled", text="ERRO: SEM ARQUIVO DE DADOS", fg_color="red")
        else:
             self.btn_acao.configure(state="normal", text="CONFIGURAR TOKENS", fg_color="#FF9800", hover_color="#F57C00")

    def atualizar_ui_pronto(self, txt):
        self.lbl_icon.configure(text="✅", text_color="#4CAF50")
        self.lbl_status_main.configure(text="Token Configurado", text_color="#4CAF50")
        self.lbl_detalhes.configure(text=txt)
        self.status_frame.configure(border_color="#4CAF50", border_width=2)
        self.btn_acao.configure(state="disabled", text="PRONTO PARA USO", fg_color="#4CAF50")

    def atualizar_ui_erro(self, msg):
        self.lbl_icon.configure(text="🚫", text_color="red")
        self.lbl_status_main.configure(text="Erro de Driver", text_color="red")
        self.lbl_detalhes.configure(text=msg)

    # --- AÇÃO ---
    def iniciar_lote(self):
        if MODO_SEGURO:
            messagebox.showerror("Erro de Configuração", "Arquivo 'segredos.py' não encontrado!\nCrie o arquivo com LABEL_REAL, PUK_REAL e PIN_REAL.")
            return

        self.processando = True
        self.btn_acao.configure(state="disabled", text="PROCESSANDO...", fg_color="#1F6AA5")
        self.progressbar.place(relx=0.5, rely=0.90, anchor="center")
        self.progressbar.start()
        threading.Thread(target=self.executar_lote).start()

    def executar_lote(self):
        log = ""
        sucesso = False
        for slot in self.lista_slots:
            time.sleep(0.5)
            try:
                try:
                    if self.pkcs11.getTokenInfo(slot).label.startswith(LABEL_VISUAL): continue
                except: pass

                self.pkcs11.initToken(slot, PUK_FINAL, LABEL_FINAL)
                sess = self.pkcs11.openSession(slot, CKF_SERIAL_SESSION | CKF_RW_SESSION)
                sess.login(PUK_FINAL, CKU_SO)
                sess.initPin(PIN_FINAL)
                sess.logout()
                sess.closeSession()
                sucesso = True
            except Exception as e:
                log += f"Erro: {e}\n"

        self.processando = False
        self.progressbar.stop()
        self.progressbar.place_forget()
        
        if log: messagebox.showerror("Erros", log)
        elif sucesso: messagebox.showinfo("Sucesso", f"Token Configurado!\nNome: {LABEL_VISUAL}")

if __name__ == "__main__":
    app = App()
    app.mainloop()