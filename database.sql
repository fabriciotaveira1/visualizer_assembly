-- =============================
-- EXTENSÕES
-- =============================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================
-- CONDOMÍNIO
-- =============================
CREATE TABLE condominios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================
-- CONFIGURAÇÕES
-- =============================
CREATE TABLE configuracoes_condominio (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominio_id UUID REFERENCES condominios(id),

    tipo_votacao_padrao TEXT, -- unidade | fracao
    quorum_minimo NUMERIC,
    tempo_votacao_padrao INTEGER,
    tempo_fala_padrao INTEGER,
    limite_procuracoes INTEGER,

    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================
-- USUÁRIOS
-- =============================
CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominio_id UUID,
    nome TEXT,
    email TEXT UNIQUE,
    senha_hash TEXT,
    perfil TEXT, -- admin, operador, sindico
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================
-- UNIDADES
-- =============================
CREATE TABLE unidades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominio_id UUID REFERENCES condominios(id),

    bloco TEXT,
    numero TEXT,

    identificador_externo TEXT, -- chave para importação
    fracao_ideal NUMERIC NULL,

    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE (condominio_id, identificador_externo)
);

-- =============================
-- MORADORES
-- =============================
CREATE TABLE moradores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominio_id UUID REFERENCES condominios(id),
    unidade_id UUID REFERENCES unidades(id),

    nome TEXT NOT NULL,
    cpf TEXT,
    telefone TEXT,
    email TEXT,
    tipo TEXT, -- proprietario, inquilino

    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================
-- ASSEMBLEIAS
-- =============================
CREATE TABLE assembleias (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominio_id UUID REFERENCES condominios(id),

    titulo TEXT,
    data DATE,

    status TEXT, -- criada, aberta, em_andamento, encerrada, finalizada

    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================
-- PAUTAS
-- =============================
CREATE TABLE pautas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assembleia_id UUID REFERENCES assembleias(id),

    titulo TEXT,
    descricao TEXT,

    tipo_votacao TEXT, -- unidade | fracao
    regra_votacao TEXT, -- simples, 2_3, unanimidade

    ordem INTEGER,
    status TEXT, -- aguardando, em_votacao, encerrada

    versao INTEGER DEFAULT 1,
    bloqueada BOOLEAN DEFAULT FALSE,
    modo_votacao TEXT DEFAULT 'manual', -- manual, importado, resultado_manual

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE opcoes_votacao (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pauta_id UUID REFERENCES pautas(id) NOT NULL,
    codigo INTEGER NOT NULL,
    descricao TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (pauta_id, codigo)
);

-- =============================
-- PRESENÇA
-- =============================
CREATE TABLE presencas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assembleia_id UUID REFERENCES assembleias(id),
    unidade_id UUID REFERENCES unidades(id),

    tipo TEXT, -- presente, procuracao

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE (assembleia_id, unidade_id)
);

-- =============================
-- PROCURAÇÕES
-- =============================
CREATE TABLE procuracoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assembleia_id UUID REFERENCES assembleias(id),

    unidade_origem_id UUID REFERENCES unidades(id),
    unidade_destino_id UUID REFERENCES unidades(id),

    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================
-- VOTOS
-- =============================
CREATE TABLE votos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    pauta_id UUID REFERENCES pautas(id),
    unidade_id UUID REFERENCES unidades(id),

    voto TEXT, -- sim, nao, abstencao

    tipo_voto TEXT, -- direto, procuracao
    tipo_origem TEXT, -- manual, importado
    codigo_opcao INTEGER,
    descricao_opcao TEXT,
    peso NUMERIC,
    ip TEXT,
    data_voto TIMESTAMP,

    registrado_por UUID REFERENCES usuarios(id),

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE (pauta_id, unidade_id)
);

CREATE TABLE resultados_manuais (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pauta_id UUID REFERENCES pautas(id) NOT NULL,
    codigo_opcao INTEGER NOT NULL,
    descricao_opcao TEXT NOT NULL,
    quantidade_votos INTEGER NOT NULL,
    peso_total NUMERIC NOT NULL,
    percentual NUMERIC NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================
-- AUDITORIA
-- =============================
CREATE TABLE auditoria_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    usuario_id UUID REFERENCES usuarios(id),
    acao TEXT,
    entidade TEXT,
    entidade_id UUID,

    dados JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================
-- IMPORTAÇÃO
-- =============================
CREATE TABLE importacoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominio_id UUID REFERENCES condominios(id),

    tipo TEXT, -- unidades, moradores
    arquivo_nome TEXT,

    status TEXT,
    erros JSONB,
    quantidade_processada INTEGER DEFAULT 0,
    quantidade_sucesso INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================
-- MAPEAMENTO DE IMPORTAÇÃO
-- =============================
CREATE TABLE importacao_mapeamentos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    condominio_id UUID REFERENCES condominios(id),

    campo_origem TEXT,
    campo_destino TEXT
);

-- =============================
-- RESULTADOS CACHE (PERFORMANCE)
-- =============================
CREATE TABLE resultados_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    pauta_id UUID REFERENCES pautas(id),

    total_votos INTEGER,
    total_peso NUMERIC,

    resultado JSONB,

    updated_at TIMESTAMP DEFAULT NOW()
);

-- =============================
-- DASHBOARD
-- =============================
CREATE TABLE dashboard_metricas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    condominio_id UUID REFERENCES condominios(id),

    total_assembleias INTEGER,
    total_votos INTEGER,

    updated_at TIMESTAMP DEFAULT NOW()
);

-- =============================
-- ATA
-- =============================
CREATE TABLE atas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    assembleia_id UUID REFERENCES assembleias(id),

    conteudo TEXT,
    gerada BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================
-- ÍNDICES (PERFORMANCE)
-- =============================
CREATE INDEX idx_unidades_condominio ON unidades(condominio_id);
CREATE INDEX idx_moradores_unidade ON moradores(unidade_id);
CREATE INDEX idx_votos_pauta ON votos(pauta_id);
CREATE INDEX idx_presenca_assembleia ON presencas(assembleia_id);
CREATE INDEX idx_pautas_assembleia ON pautas(assembleia_id);
