# language: pt
Funcionalidade: Verificação de saúde
  Para que a plataforma saiba se o serviço pode receber tráfego
  O serviço expõe uma verificação de saúde

  Cenário: Serviço disponível
    Dado que o serviço está no ar
    Quando consulto a verificação de saúde
    Então recebo o status "ok"
