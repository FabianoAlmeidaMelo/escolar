-- View: public.view_inadimplentes

-- DROP VIEW public.view_inadimplentes;

CREATE OR REPLACE VIEW view_inadimplentes AS 
 SELECT pagamento.escola_id,
    pagamento.contrato_id,
    count(pagamento.id) AS pagamentos_atrasados,
    sum(pagamento.valor) AS valor,
    sum(
        CASE
            WHEN pagamento.categoria_id = 1 THEN pagamento.valor * contratoaluno.multa / 100::numeric
            ELSE 0::numeric
        END) AS multa,
    sum(
        CASE
            WHEN pagamento.categoria_id = 1 THEN contratoaluno.juros / 30::numeric * (now()::date - pagamento.data)::numeric / 100::numeric * pagamento.valor
            ELSE 0::numeric
        END) AS juros,
    pessoa.cpf,
    pessoa.nome,
    pessoa.celular,
    pessoa.email
   FROM financeiro_pagamento pagamento
     LEFT JOIN financeiro_contrato contrato ON contrato.id = pagamento.contrato_id
     LEFT JOIN financeiro_contratoaluno contratoaluno ON contratoaluno.contrato_ptr_id = contrato.id
     LEFT JOIN escolas_membrofamilia membro_familia ON membro_familia.pessoa_ptr_id = contratoaluno.responsavel_id
     LEFT JOIN escolas_pessoa pessoa ON pessoa.id = contratoaluno.responsavel_id
  WHERE pagamento.efet = false AND pagamento.data >= date_trunc('year'::text, now()) AND pagamento.data < now()::date
  GROUP BY pagamento.escola_id, pagamento.contrato_id, pessoa.cpf, pessoa.nome, pessoa.celular, pessoa.email;
