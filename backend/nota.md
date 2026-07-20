# Anotações

```txt
* No "Exames Solicitados" são todos os registros que estão no nosso banco de dados.
* No "Realizados Internamente" são exames lançados pelo SPDATA.
* Na "Taxa de Conversão" é a porcetagem conversão.
```

---

Tabela	Papel
SILANEXA	Tabela principal. Representa o lançamento/solicitação do exame no SPDATA. Cada linha aqui está sendo contada como 1 exame solicitado.
SICADATE	Conta/atendimento ligado ao exame. Traz convênio, guia, senha, prontuário, médico/solicitante da conta e vínculo com atendimento.
TBCONVEN	Cadastro do convênio. Usada para pegar nome do convênio e tabela de valores usada pelo convênio.
ATCABECATEND	Cabeçalho do atendimento. Ajuda a encontrar o paciente real vinculado ao atendimento.
RICADPAC	Cadastro de pacientes. Aparece duas vezes na query: uma pelo atendimento e outra pelo prontuário. Traz nome, CPF e celular.
SIREFCON	Referência do exame por convênio. Mapeia o exame interno para o código usado pelo convênio/TUSS/AMB.
SITABPRO	Cadastro do procedimento/exame. Traz nome do exame, código alfanumérico CODALF e código CODAMB.
PRSITEXAME	Cadastro/status do exame. Traz o nome do status do exame no SPDATA.
TBESPEC	Cadastro de especialidades. Traz a especialidade vinculada ao exame.
TBVLRTHM	Tabela de valores. Usada para calcular o valor estimado do exame pelo código e pela tabela do convênio.
Relação principal:
SILANEXA
  -> SICADATE
  -> TBCONVEN
  -> RICADPAC / ATCABECATEND
  -> SIREFCON
  -> SITABPRO
  -> PRSITEXAME
  -> TBESPEC
  -> TBVLRTHM

  
Em termos práticos:
SILANEXA diz qual exame foi lançado.  
SICADATE diz em qual atendimento/conta ele aconteceu.  
RICADPAC diz quem é o paciente.  
TBCONVEN diz qual convênio.  
SITABPRO diz qual é o nome/cadastro do exame.  
SIREFCON diz qual código do convênio/TUSS usar.  
TBVLRTHM diz quanto esse exame vale estimadamente.