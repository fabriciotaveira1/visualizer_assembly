# 📜 REGRAS DE NEGÓCIO – SISTEMA DE ASSEMBLEIAS

## 🎯 OBJETIVO

Definir todas as regras operacionais, funcionais e legais do sistema de gestão de assembleias.

---

# 🧠 1. REGRAS GERAIS

1.1 Todo dado pertence obrigatoriamente a um condomínio.
1.2 Não é permitido compartilhar dados entre condomínios.
1.3 Uma assembleia pertence a apenas um condomínio.
1.4 Todas as entidades (unidade, pessoa, pauta, voto) devem estar vinculadas ao mesmo condomínio.

---

# 🔐 2. AUTENTICAÇÃO E PERMISSÕES

2.1 O sistema deve utilizar autenticação via JWT.
2.2 Deve existir controle de permissões (RBAC).

Perfis:

* ADMIN → acesso total
* OPERADOR → gerencia assembleias
* SÍNDICO → visualização e acompanhamento
* MORADOR → votação (futuro)

2.3 Toda ação deve estar vinculada a um usuário autenticado.

---

# 🧾 3. AUDITORIA

3.1 Todo voto deve registrar:

* Usuário responsável
* Data/hora
* Tipo (direto / procuração)

3.2 Toda ação crítica deve ser registrada:

* Abertura de assembleia
* Início de pauta
* Encerramento de votação
* Reabertura de pauta

3.3 Nenhum registro de auditoria pode ser alterado ou excluído.

---

# 🧠 4. ASSEMBLEIA

4.1 Estados possíveis:

* CRIADA
* ABERTA
* EM_ANDAMENTO
* ENCERRADA
* FINALIZADA

4.2 Não é permitido votar se a assembleia não estiver ativa.

4.3 Após FINALIZADA, não pode haver alterações.

---

# 📋 5. PAUTAS

5.1 Pautas são editáveis apenas antes de iniciar votação.
5.2 Após iniciar votação, a pauta deve ser bloqueada.
5.3 Deve existir versionamento de pautas.
5.4 Deve ser possível reabrir pauta com registro de auditoria.

---

# 🗳️ 6. VOTAÇÃO

6.1 Cada unidade pode votar apenas uma vez por pauta.
6.2 Tipos de voto:

* DIRETO
* POR PROCURAÇÃO

6.3 Só pode votar se:

* Estiver presente OU
* Possuir procuração válida

6.4 Não permitir voto após encerramento da pauta.
6.5 Sistema deve impedir duplicidade (inclusive concorrência).

---

# ⚖️ 7. REGRAS DE VOTAÇÃO

7.1 Tipos suportados:

* Por unidade
* Por fração ideal

7.2 Regras avançadas:

* Maioria simples
* 2/3
* Unanimidade

7.3 O sistema deve calcular automaticamente o resultado.

---

# 📊 8. QUÓRUM

8.1 O sistema deve calcular:

* Número de presentes
* Fração ideal presente

8.2 A votação só pode iniciar se atingir quórum mínimo.
8.3 O quórum deve ser configurável por condomínio.

---

# 👥 9. PRESENÇA

9.1 Tipos:

* Presente
* Representado por procuração

9.2 Apenas presença física entra na lista oficial.
9.3 Procuração não conta como presença física.

9.4 O sistema deve indicar:

* Quem não votou
* Quem está ausente
* Quem está representado

---

# 📄 10. PROCURAÇÃO

10.1 Uma unidade pode representar outra.
10.2 Deve existir limite configurável de procurações.
10.3 Procuração deve estar vinculada à assembleia.
10.4 Procuração não substitui presença física.

---

# ⏱️ 11. TEMPO

11.1 Cada pauta pode ter tempo de votação.
11.2 Deve existir cronômetro visível no telão.
11.3 Sistema pode encerrar automaticamente ao atingir o tempo.

11.4 Deve existir cronômetro de fala:

* Controle de tempo de moradores
* Controle de apresentações

---

# 🖥️ 12. TELÃO

12.1 Deve exibir:

* Resultados em tempo real
* Percentuais
* Status da votação

12.2 Modos:

* Votação
* Aguardando
* Mensagem personalizada

12.3 Atualização via WebSocket.

---

# 📊 13. RESULTADOS

13.1 Devem ser calculados em tempo real.
13.2 Devem considerar:

* Peso por fração ideal
* Quantidade de votos

13.3 Deve identificar:

* Vencedor
* Empate

---

# 🧾 14. RELATÓRIOS

14.1 Tipos:

* Sintético
* Analítico
* Ata automática

14.2 A ata deve conter:

* Presença
* Quórum
* Resultado por pauta

14.3 Exportações:

* PDF
* CSV
* Pacote completo

---

# 📦 15. ATA AUTOMÁTICA

15.1 Deve ser gerada automaticamente ao final da assembleia.
15.2 Deve refletir fielmente os dados registrados.
15.3 Não pode ser editada após geração final.

---

# ⚙️ 16. CONFIGURAÇÕES

16.1 Cada condomínio pode definir:

* Tipo de votação padrão
* Quórum mínimo
* Tempo de votação
* Tempo de fala

---

# 📥 17. IMPORTAÇÃO

17.1 Deve permitir importação de moradores via CSV.
17.2 Dados devem ser validados antes de salvar.
17.3 Dados duplicados devem ser tratados.

---

# 🚨 18. CONTINGÊNCIA

18.1 Sistema deve funcionar offline (modo contingência).
18.2 Votos devem ser sincronizados posteriormente.
18.3 Nenhum dado pode ser perdido.

---

# 🔄 19. BACKUP

19.1 Deve existir backup automático.
19.2 Deve ser possível restaurar assembleias.

---

# 📊 20. DASHBOARD

20.1 Deve apresentar:

* Número de assembleias
* Total de votos
* Estatísticas operacionais

---

# 📱 21. MOBILE READY

21.1 API deve ser REST e versionada.
21.2 Sistema deve ser desacoplado (backend/frontend).

---

# 🔗 22. MULTI-ASSEMBLEIA

22.1 Sistema deve suportar múltiplas assembleias simultâneas.
22.2 Cada assembleia deve ser isolada.

---

# 🧩 23. CONFIGURAÇÕES AVANÇADAS

23.1 Templates de assembleia
23.2 Configurações por condomínio
23.3 Regras personalizadas

---

# 🔐 24. LGPD

24.1 Dados pessoais devem ser protegidos.
24.2 Acesso restrito por perfil.
24.3 Logs de acesso obrigatórios.

---

# 🚫 25. BLOQUEIOS OPERACIONAIS

25.1 Não permitir:

* Votação sem quórum
* Voto duplicado
* Alterações após encerramento

---

# 🔄 26. REABERTURA DE PAUTA

26.1 Deve ser permitida apenas com auditoria.
26.2 Deve invalidar votos anteriores (opcional configurável).

---

# 🧪 27. MODO TESTE

27.1 Deve permitir simulação completa.
27.2 Não deve impactar dados reais.

---

28. IMPORTAÇÃO AVANÇADA

28.1 O sistema deve aceitar múltiplos formatos de CSV
28.2 Fração ideal é opcional
28.3 Campos desconhecidos devem ser ignorados
28.4 Dados devem ser normalizados antes de salvar
28.5 Deve existir log de importação
28.6 Deve permitir reprocessamento

# 🏁 CONCLUSÃO

Estas regras são obrigatórias e devem ser respeitadas em toda implementação do sistema.

---
