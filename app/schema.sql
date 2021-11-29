BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "tipos_equipamento" (
	"id"	INTEGER NOT NULL,
	"nome"	VARCHAR(20) NOT NULL UNIQUE,
	"qtd_disponivel"	INTEGER NOT NULL,
	"ativo"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "equipamentos" (
	"id"	INTEGER NOT NULL,
	"patrimonio"	VARCHAR(20) NOT NULL,
	"descricao"	VARCHAR(50) NOT NULL,
	"tipo_eqp_id"	INTEGER NOT NULL,
	"data_cadastro"	DATETIME NOT NULL,
	"data_atualizacao"	DATETIME,
	"status"	VARCHAR(20) NOT NULL,
	"motivo_indisponibilidade"	TEXT,
	"ativo"	BOOLEAN NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	UNIQUE("patrimonio"),
	FOREIGN KEY("tipo_eqp_id") REFERENCES "tipos_equipamento"("id")
);
CREATE TABLE IF NOT EXISTS "salas" (
	"id"	INTEGER NOT NULL,
	"numero"	VARCHAR(20) NOT NULL,
	"setor"	VARCHAR(20) NOT NULL,
	"qtd_aluno"	INTEGER NOT NULL,
	"data_cadastro"	DATETIME NOT NULL,
	"status"	VARCHAR(20) NOT NULL,
	"motivo_indisponibilidade"	TEXT,
	"ativo"	BOOLEAN NOT NULL,
	"data_atualizacao"	DATETIME,
	PRIMARY KEY("id" AUTOINCREMENT),
	UNIQUE("numero")
);
CREATE TABLE IF NOT EXISTS "solicitacao_equipamento" (
	"solicitacao_id"	INTEGER,
	"equipamento_id"	INTEGER,
	PRIMARY KEY("solicitacao_id","equipamento_id"),
	FOREIGN KEY("equipamento_id") REFERENCES "equipamentos"("id"),
	FOREIGN KEY("solicitacao_id") REFERENCES "solicitacoes"("id")
);
CREATE TABLE IF NOT EXISTS "solicitacoes" (
	"id"	INTEGER NOT NULL,
	"tipo"	VARCHAR(20) NOT NULL,
	"turno"	VARCHAR(20) NOT NULL,
	"status"	VARCHAR(20) NOT NULL,
	"qtd_equipamento"	INTEGER,
	"data_abertura"	DATETIME NOT NULL,
	"data_preferencial"	DATETIME,
	"data_entrega"	DATETIME,
	"data_devolucao"	DATETIME,
	"data_cancelamento"	DATETIME,
	"data_finalizacao"	DATETIME,
	"usuario_id"	INTEGER NOT NULL,
	"sala_id"	INTEGER,
	"tipo_eqp_id"	INTEGER,
	"ativo"	BOOLEAN NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("tipo_eqp_id") REFERENCES "tipos_equipamento"("id"),
	FOREIGN KEY("usuario_id") REFERENCES "usuarios"("id"),
	FOREIGN KEY("sala_id") REFERENCES "salas"("id")
);
CREATE TABLE IF NOT EXISTS "posts" (
	"id"	INTEGER NOT NULL,
	"titulo"	VARCHAR(100) NOT NULL,
	"data_postado"	DATETIME NOT NULL,
	"data_atualizacao"	INTEGER,
	"conteudo"	TEXT NOT NULL,
	"usuario_id"	INTEGER NOT NULL,
	"ativo"	BOOLEAN NOT NULL,
	PRIMARY KEY("id"),
	FOREIGN KEY("usuario_id") REFERENCES "usuarios"("id")
);
CREATE TABLE IF NOT EXISTS "relatorios" (
	"id"	INTEGER NOT NULL,
	"tipo"	VARCHAR(20) NOT NULL,
	"conteudo"	TEXT NOT NULL,
	"manutencao"	BOOLEAN NOT NULL,
	"defeito"	BOOLEAN NOT NULL,
	"reforma"	BOOLEAN,
	"detalhes"	TEXT,
	"status"	VARCHAR(20) NOT NULL,
	"data_abertura"	DATETIME NOT NULL,
	"data_atualizacao"	DATETIME,
	"data_finalizacao"	DATETIME,
	"usuario_id"	INTEGER NOT NULL,
	"equipamento_id"	INTEGER,
	"sala_id"	INTEGER,
	"ativo"	BOOLEAN NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("usuario_id") REFERENCES "usuarios"("id"),
	FOREIGN KEY("sala_id") REFERENCES "salas"("id"),
	FOREIGN KEY("equipamento_id") REFERENCES "equipamentos"("id")
);
CREATE TABLE IF NOT EXISTS "usuarios" (
	"id"	INTEGER NOT NULL,
	"nome"	VARCHAR(100) NOT NULL,
	"identificacao"	VARCHAR(20) NOT NULL,
	"email"	VARCHAR(100) NOT NULL,
	"senha"	VARCHAR(60) NOT NULL,
	"data_cadastro"	DATETIME NOT NULL,
	"data_atualizacao"	DATETIME,
	"imagem_perfil"	VARCHAR(20) NOT NULL,
	"admin"	BOOLEAN,
	"ativo"	BOOLEAN NOT NULL,
	PRIMARY KEY("id"),
	UNIQUE("identificacao"),
	UNIQUE("email")
);
COMMIT;
