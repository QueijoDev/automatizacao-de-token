# 🛡️ Configurador Automático de Token (SafeSign/G&D)

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Platform](https://img.shields.io/badge/Plataforma-Windows-lightgrey.svg)
![Status](https://img.shields.io/badge/Status-Estável-green.svg)

Uma ferramenta robusta de automação (RPA) desenvolvida para **configurar, formatar e inicializar** tokens criptográficos G&D (modelos SafeSign) de forma massiva e à prova de falhas.

A ferramenta comunica diretamente com os drivers PKCS#11, eliminando a necessidade de cliques manuais e contornando limitações de segurança do Windows automaticamente.

---

## 🚀 Funcionalidades

* **⚡ Zero-Click Config:** Detecta o token conectado e configura automaticamente.
* **🛡️ Bypass de Segurança:**
    * Auto-elevação para Administrador.
    * Correção automática do Registro do Windows (`EnableInitToken`) para permitir formatação.
    * Bypass de bloqueio "Action Prohibited" em drivers restritos.
* **🎨 Interface Moderna:** UI desenvolvida em `CustomTkinter` com modo escuro/claro e feedback visual intuitivo.
* **🔌 Multi-Token:** Suporte para múltiplos leitores USB simultâneos.
* **🧠 Inteligente:**
    * Identifica se o token é virgem (fábrica) ou já configurado.
    * Não reconfigura tokens prontos (evita acidentes).
    * Corrige automaticamente o tamanho do Label (32 caracteres) exigido pelo driver.

---

## 🛠️ Tecnologias Utilizadas

* **[Python 3.11+](https://www.python.org/)**: Linguagem base.
* **[PyKCS11](https://github.com/LudovicRousseau/PyKCS11)**: Comunicação direta com o hardware (Chip do Token).
* **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)**: Interface gráfica moderna e responsiva.
* **WinReg & Ctypes**: Manipulação de baixo nível do Windows para permissões.

---

## ⚙️ Pré-requisitos

1.  **Sistema Operacional:** Windows 10 ou 11 (64-bits).
2.  **Drivers:** SafeSign Standard (A.E.T. Europe B.V.) instalado.
    * DLL esperada: `C:\Windows\System32\aetpkss1.dll`

---

## 📦 Como Usar (Usuário Final)

1.  Baixe o executável `ConfiguradorToken.exe`.
2.  Conecte o(s) token(s) USB no computador.
3.  Execute o programa.
    * *Nota: O programa pedirá permissão de Administrador para ajustar o driver.*
4.  Aguarde o status ficar **Laranja** (Pendente).
5.  Clique em **"CONFIGURAR TOKENS"**.
6.  Aguarde a barra de progresso e o ícone ficar **Verde** ✅.

---

## 💻 Como Rodar o Código (Desenvolvedor)

### 1. Clonar o repositório
```bash
git clone [https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git](https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git)
cd SEU_REPOSITORIO