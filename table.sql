CREATE TABLE TB_ATIVOS_GALACTICOS (
    id_ativo NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR2(50),
    setor VARCHAR2(20),
    preco_base NUMBER(10,2),
    estoque NUMBER
);

INSERT INTO TB_ATIVOS_GALACTICOS (nome, setor, preco_base, estoque) 
VALUES ('Cristal de Dilítio', 'MINERAL', 500.00, 100);

INSERT INTO TB_ATIVOS_GALACTICOS (nome, setor, preco_base, estoque) 
VALUES ('Hidrogênio Metálico', 'COMBUSTIVEL', 120.00, 500);

INSERT INTO TB_ATIVOS_GALACTICOS (nome, setor, preco_base, estoque) 
VALUES ('Holodiscos de Memória', 'DADOS', 850.00, 50);

COMMIT;