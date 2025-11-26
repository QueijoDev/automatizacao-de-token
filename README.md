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

## ⚠️ Pré-requisitos Obrigatórios

Para que o software funcione, o computador **DEVE** ter o driver do token instalado. O software não instala o driver, ele apenas o utiliza.

1.  **Sistema Operacional:** Windows 10 ou 11 (64-bits).
2.  **Driver SafeSign (A.E.T. Europe):**
    * O software busca especificamente pela DLL: `C:\Windows\System32\aetpkss1.dll`
    * Certifique-se de que o "SafeSign Standard" ou o gerenciador do seu certificado digital está instalado.

---

## 🔐 Configuração de Senhas (Importante)

Por questões de segurança, **as senhas reais NÃO estão incluídas no código fonte** deste repositório.

Para que a automação funcione no seu computador, você precisa criar um arquivo de configuração manual:

1.  Na pasta raiz do projeto, crie um novo arquivo chamado **`segredos.py`**.
2.  Cole o seguinte código dentro dele e altere as senhas:

```python
# segredos.py
# Este arquivo contém as credenciais reais e NÃO é enviado ao GitHub.

# Nome que aparecerá no Token e no topo do programa
LABEL_REAL = "NOME DA SUA EMPRESA"

# Senha de Administrador (PUK/SO-PIN)
PUK_REAL = "SUA_SENHA_PUK_AQUI"

# Senha do Usuário (PIN)
PIN_REAL = "SUA_SENHA_PIN_AQUI"
