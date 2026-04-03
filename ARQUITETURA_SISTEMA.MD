# 🏗️ ARQUITETURA DO SISTEMA – GESTÃO DE ASSEMBLEIAS

## 🎯 OBJETIVO

Sistema web para gestão completa de assembleias condominiais com votação em tempo real, controle de presença, auditoria e geração de relatórios.

---

# 🧠 VISÃO GERAL

O sistema é dividido em módulos independentes, seguindo arquitetura modular (DDD simplificado).

---

# 📦 ESTRUTURA DE MÓDULOS

```
app/
│
├── auth/                # Autenticação e permissões
├── assembleia/         # Gestão de assembleias e estados
├── votacao/            # Regras de votação e votos
├── presenca/           # Presença e quórum
├── procuracao/         # Representação entre unidades
├── relatorios/         # Geração de PDFs e exports
├── telao/              # WebSocket e exibição em tempo real
├── configuracoes/      # Configurações por condomínio
├── dashboard/          # Métricas da empresa
├── auditoria/          # Logs e rastreabilidade
├── integracoes/        # Importações e exportações
├── core/               # Banco, utils, base
```

---

# 🔄 FLUXO PRINCIPAL DA ASSEMBLEIA

## 1. Criação

* Admin cria assembleia
* Define condomínio
* Define pautas (ou usa template)

---

## 2. Abertura

* Estado: `CRIADA → ABERTA`
* Sistema habilita presença

---

## 3. Registro de presença

* Unidades entram como:

  * Presente
  * Via procuração
* Sistema calcula:

  * Total presentes
  * Fração ideal presente

---

## 4. Validação de quórum

* Sistema valida regras:

  * % mínima
* Se não atingir:

  * Bloqueia votação

---

## 5. Início da pauta

* Ativa pauta
* Estado:

  * `AGUARDANDO → EM_VOTACAO`

---

## 6. Votação

* Unidade vota:

  * Direto
  * Por procuração
* Sistema valida:

  * Presença
  * Duplicidade
* Registra auditoria

---

## 7. Tempo de votação

* Cronômetro ativo
* Pode encerrar automaticamente

---

## 8. Atualização em tempo real

* WebSocket envia:

  * Resultados
  * Percentuais
* Telão atualiza

---

## 9. Encerramento da pauta

* Estado:

  * `EM_VOTACAO → ENCERRADA`
* Resultado final definido

---

## 10. Próxima pauta

* Reinicia fluxo

---

## 11. Finalização da assembleia

* Estado:

  * `ENCERRADA → FINALIZADA`
* Sistema gera:

  * Ata automática
  * Relatórios

---

# 📊 MOTOR DE VOTAÇÃO

O cálculo considera:

* Quantidade de votos
* Peso por fração ideal

Resultado:

```
- total_votos
- total_peso
- vencedores
- empate
```

---

# 🧠 REGRAS IMPORTANTES

## Votação

* 1 voto por unidade por pauta
* Unidade deve:

  * Estar presente OU
  * Ter procuração válida

## Presença

* Presença ≠ procuração
* Procuração não entra na lista física

## Auditoria

Registrar:

* Quem votou
* Tipo de voto
* Data/hora
* Operador

---

# 🔐 SEGURANÇA

* JWT para autenticação
* RBAC:

  * Admin
  * Operador
  * Síndico
  * Morador (futuro)
* Dados sensíveis protegidos (LGPD)

---

# 📡 TEMPO REAL

* WebSocket (`/ws/telao`)
* Broadcast de eventos:

```
telao_update
pauta_ativada
votacao_encerrada
```

---

# 📄 RELATÓRIOS

## Tipos

* Sintético
* Analítico
* Ata automática

## Exportação

* CSV
* PDF
* Pacote completo

---

# ⚙️ CONFIGURAÇÕES POR CONDOMÍNIO

Cada condomínio pode definir:

* Tipo de votação padrão
* Regras de quórum
* Tempo de votação
* Tempo de fala

---

# 🚨 CONTINGÊNCIA

* Votos armazenados localmente (fallback)
* Sincronização posterior

---

# 🔄 BACKUP

* Backup automático do banco
* Exportação manual da assembleia

---

# 📱 PREPARAÇÃO PARA MOBILE

* API REST versionada:

```
/api/v1/
```

* Separação backend/frontend
* Stateless

---

# 🧩 EVENTOS DO SISTEMA

```
ASSEMBLEIA_CRIADA
ASSEMBLEIA_ABERTA
PRESENCA_REGISTRADA
QUORUM_ATINGIDO
PAUTA_ATIVADA
VOTO_REGISTRADO
PAUTA_ENCERRADA
ASSEMBLEIA_FINALIZADA
```

---

# 🧠 ESCALABILIDADE

* Redis (cache)
* Filas (relatórios)
* WebSocket distribuído

---

# 🧪 MODO TESTE

* Simulação de assembleia
* Dados fictícios

---

# 🏁 CONCLUSÃO

Este sistema foi projetado para:

✔ Operação real de assembleias
✔ Segurança jurídica
✔ Escalabilidade para SaaS
✔ Integração futura com mobile

---
