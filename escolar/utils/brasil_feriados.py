# -*- coding: utf-8 -*-
import json
import requests

####  http://www.calendario.com.br/api_feriados_municipais_estaduais_nacionais.php

# Você pode utilizar nossa api através do link abaixo, substituindo o ANO, ESTADO e CIDADE, pelos desejados:
# https://api.calendario.com.br/?ano=2017&estado=SP&cidade=SAO_PAULO&token=ZmFsbWVpZGFtZWxvQHVvbC5jb20uYnImaGFzaD0xOTU2OTg2MTc=

# Pode também utilizar o Código IBGE da cidade desejada:
# https://api.calendario.com.br/?ano=2017&ibge=3550308&token=ZmFsbWVpZGFtZWxvQHVvbC5jb20uYnImaGFzaD0xOTU2OTg2MTc=

# Você receberá um resultado em XML, semelhante a esta imagem:
# http://www.calendario.com.br/figs/xml_sample.png

# Se preferir o resultado em JSON, basta incluir o parametro json=true na URL:
# https://api.calendario.com.br/?json=true&ano=2017&ibge=3550308&token=ZmFsbWVpZGFtZWxvQHVvbC5jb20uYnImaGFzaD0xOTU2OTg2MTc=

# Para acessar a lista de cidades do Banco de Dados, utilize esse link:
# http://www.calendario.com.br/api/cities.json

# Veja mais informações nesta página:
# http://www.calendario.com.br/dev/api_feriados_municipais_estaduais_nacionais.php

# atenciosamente,
# equipe Calendario.com.br


# from datetime import date, datetime
# import time


# DATE_FTMS = ('%Y%m%d', '%d/%m/%Y', '%d/%m/%Y %H:%M', '%d/%m/%Y %H:%M:%S',)


# def get_date(value, formats=DATE_FTMS):
#     date_value = None
#     if value:  # pode vir None do Protheus
#         for fmt in formats:
#             try:
#                 date_value = date(*time.strptime(value, fmt)[:3])
#                 break
#             except ValueError:
#                 pass
#     return date_value


def CONSULTA(ano, codigo_ibge):
    """
    ref #47
    achar os dias úteis
    ex: CONSULTA(2018, 3549904)
    """
    url = u'https://api.calendario.com.br/?ano=%s&&ibge=%s&json=true&token=ZmFsbWVpZGFtZWxvQHVvbC5jb20uYnImaGFzaD0xOTU2OTg2MTc='  % (ano, codigo_ibge)
    response = requests.get(url)
    json_data = json.loads(response.text)

    return json_data


[{'date': '01/01/2018',
  'description': 'O Ano-Novo ou Réveillon é um evento que acontece quando uma cultura celebra o fim de um ano e o começo do próximo. A celebração do evento é também chamada Réveillon, termo oriundo do verbo francês réveiller, que em português significa DESPERTAR',
  'link': 'http://www.calendario.com.br/feriados-nacionais/ano-novo.php',
  'name': 'Ano Novo',
  'type': 'Feriado Nacional',
  'type_code': '1'},
 {'date': '12/02/2018',
  'description': 'Ponto Facultativo, ou seja, cabe às empresas e orgão públicos decidirem se trabalharão ou não.',
  'link': 'http://www.calendario.com.br/feriados-nacionais/carnaval.php',
  'name': 'Carnaval',
  'type': 'Facultativo',
  'type_code': '4'},
 {'date': '13/02/2018',
  'description': 'Carnaval NÃO é um feriado oficial, é Ponto Facultativo, ou seja, cabe às empresas e orgão públicos decidirem se trabalharão ou não.',
  'link': 'http://www.calendario.com.br/feriados-nacionais/carnaval.php',
  'name': 'Carnaval',
  'type': 'Facultativo',
  'type_code': '4'},
 {'date': '14/02/2018',
  'description': 'Ponto Facultativo até às 14h.',
  'link': 'http://www.calendario.com.br/feriados-nacionais/carnaval.php',
  'name': 'Carnaval',
  'type': 'Facultativo',
  'type_code': '4'},
 {'date': '19/03/2018',
  'description': 'De acordo com a Lei nº 8821, de 27/11/2012',
  'link': ' https://www.leismunicipais.com.br/a/sp/s/sao-jose-dos-campos/lei-ordinaria/2012/882/8821/lei-ordinaria-n-8821-2012-institui-o-dia-19-de-marco-feriado-municipal-em-homenagem-ao-padroeiro-de-sao-jose-dos-campos.html',
  'name': 'Dia de São José, Padroeiro da Cidade - Lei  2.096, de 30/11/2012',
  'raw_description': 'De acordo com a Lei nº 8821, de 27/11/2012',
  'type': 'Feriado Municipal',
  'type_code': 3},
 {'date': '30/03/2018',
  'description': 'Também chamada de "Sexta Feira da Paixão" é a sexta-feira que ocorre antes do domingo de Páscoa, e é o dia que os cristãos lembram da crucificação de Cristo.',
  'link': 'http://www.calendario.com.br/feriados-nacionais/sexta-feira-santa.php',
  'name': 'Sexta-Feira Santa',
  'type': 'Feriado Nacional',
  'type_code': '1'},
 {'date': '30/03/2018',
  'description': '',
  'link': '',
  'name': 'Sexta-feira Santa',
  'raw_description': '',
  'type': 'Feriado Municipal',
  'type_code': 3},
 {'date': '01/04/2018',
  'description': 'A Páscoa é um evento religioso cristão, normalmente considerado pelas igrejas ligadas a esta corrente religiosa como a maior e a mais importante festa da Cristandade. Na Páscoa os cristãos celebram a Ressurreição de Jesus Cristo depois da sua morte.',
  'link': '',
  'name': 'Páscoa',
  'type': 'Dia Convencional',
  'type_code': '9'},
 {'date': '21/04/2018',
  'description': 'Joaquim José da Silva Xavier, o Tiradentes foi um dentista, tropeiro, minerador, comerciante, militar e ativista político. É reconhecido como mártir da Inconfidência Mineira e herói nacional. O dia de sua execução, 21 de abril, é feriado nacional.',
  'link': 'http://www.calendario.com.br/feriados-nacionais/dia-de-tiradentes.php',
  'name': 'Dia de Tiradentes',
  'type': 'Feriado Nacional',
  'type_code': '1'},
 {'date': '01/05/2018',
  'description': 'O Dia do Trabalhador ou Dia Internacional dos Trabalhadores é celebrado anualmente no dia 1º de Maio em numerosos países do mundo, sendo feriado no Brasil, em Portugal e em outros países.',
  'link': 'http://www.calendario.com.br/feriados-nacionais/dia-do-trabalho.php',
  'name': 'Dia do Trabalho',
  'type': 'Feriado Nacional',
  'type_code': '1'},
 {'date': '13/05/2018',
  'description': 'O Dia das Mães teve a sua origem no princípio do século XX, quando uma jovem norte-americana, Anna Jarvis, perdeu sua mãe e entrou em completa depressão. Preocupadas com aquele sofrimento, algumas amigas tiveram a ideia de criar uma data para comemorar o dia das mães.',
  'link': '',
  'name': 'Dia das Mães',
  'type': 'Dia Convencional',
  'type_code': '9'},
 {'date': '31/05/2018',
  'description': 'Ponto Facultativo no País, mas Feriado Municipal em algumas cidades.. Corpus Christi, expressão latina que significa Corpo de Cristo, é uma festa Cristã realizada na quinta-feira seguinte ao domingo da Santíssima Trindade.',
  'link': 'http://www.calendario.com.br/feriados-nacionais/corpus-christi.php',
  'name': 'Corpus Christi',
  'type': 'Facultativo',
  'type_code': '4'},
 {'date': '31/05/2018',
  'description': '',
  'link': '',
  'name': 'Corpus Christi',
  'raw_description': '',
  'type': 'Feriado Municipal',
  'type_code': 3},
 {'date': '12/06/2018',
  'description': 'O Dia dos Namorados ou Dia de São Valentim é uma data comemorativa na qual se celebra a união amorosa entre casais sendo comum a troca de cartões e presentes.',
  'link': '',
  'name': 'Dia dos Namorados',
  'type': 'Dia Convencional',
  'type_code': '9'},
 {'date': '09/07/2018',
  'description': 'A Revolução Constitucionalista de 1932 foi um movimento armado que tinha por objetivo a derrubada do Governo Provisório de Getúlio Vargas e a promulgação de uma nova constituição para o Brasil.',
  'link': '',
  'name': 'Revolução Constitucionalista',
  'raw_description': 'A Revolução Constitucionalista de 1932 foi um movimento armado que tinha por objetivo a derrubada do Governo Provisório de Getúlio Vargas e a promulgação de uma nova constituição para o Brasil.',
  'type': 'Feriado Estadual',
  'type_code': '2'},
 {'date': '27/07/2018',
  'description': ' https://www.leismunicipais.com.br/a/sp/s/sao-jose-dos-campos/lei-ordinaria/1967/132/1324/lei-ordinaria-n-1324-1967-dispoe-sobre-os-feriados-locais.html',
  'link': '',
  'name': 'Data de Fundação da Cidade - Lei 1324, DE 23/02/1967',
  'raw_description': ' https://www.leismunicipais.com.br/a/sp/s/sao-jose-dos-campos/lei-ordinaria/1967/132/1324/lei-ordinaria-n-1324-1967-dispoe-sobre-os-feriados-locais.html',
  'type': 'Feriado Municipal',
  'type_code': 3},
 {'date': '12/08/2018',
  'description': 'Em 1909, nos Estados Unidos, Sonora Luise resolveu criar um dia dedicado aos pais, motivada pela admiração que sentia pelo seu pai, William Jackson Smart. O interesse pela data difundiu-se da cidade de Spokane para todo o Estado de Washington e para o Mundo.',
  'link': '',
  'name': 'Dia dos Pais',
  'type': 'Dia Convencional',
  'type_code': '9'},
 {'date': '07/09/2018',
  'description': 'O Dia da Indepência do Brasil, oficialmente a data comemorada é a de 7 de setembro de 1822, em que ocorreu o chamado "Grito do Ipiranga".',
  'link': 'http://www.calendario.com.br/feriados-nacionais/independencia-do-brasil.php',
  'name': 'Independência do Brasil',
  'type': 'Feriado Nacional',
  'type_code': '1'},
 {'date': '12/10/2018',
  'description': 'Nossa Senhora da Conceição Aparecida é a padroeira do Brasil. Sua festa é celebrada em 12 de outubro, um feriado nacional desde que o Papa João Paulo II consagrou a Basílica em 1980.',
  'link': 'http://www.calendario.com.br/feriados-nacionais/nossa-senhora-aparecida.php',
  'name': 'Nossa Senhora Aparecida',
  'type': 'Feriado Nacional',
  'type_code': '1'},
 {'date': '15/10/2018',
  'description': 'FERIADO ESCOLAR - No dia 15 de outubro de 1827 (dia consagrado à educadora Santa Teresa de Ávila), o Imperador do Brasil, Pedro I,  baixou um Decreto Imperial que criou o Ensino Elementar no Brasil. Pelo decreto, "todas as cidades, vilas e lugarejos teriam suas escolas de primeiras letras"',
  'link': 'http://www.calendario.com.br/docs/dia-do-professor.html',
  'name': 'Dia do Professor',
  'type': 'Facultativo',
  'type_code': '4'},
 {'date': '17/10/2018',
  'description': 'Comemoração do dia do comércio. Em algumas cidades do Brasil o comércio poderá fechar, dependendo de acordos entre os sindicatos e patrões.',
  'link': '',
  'name': 'Dia do Comércio',
  'type': 'Dia Convencional',
  'type_code': '9'},
 {'date': '28/10/2018',
  'description': 'O dia do servidor público é feriado apenas para funcionários públicos.',
  'link': '',
  'name': 'Dia do Servidor Público',
  'type': 'Facultativo',
  'type_code': '4'},
 {'date': '02/11/2018',
  'description': 'O Dia de Finados ou Dia dos Fiéis Defuntos, (conhecido ainda como Dia dos Mortos no México), é celebrado pela Igreja Católica no dia 2 de novembro e é Feriado Nacional.',
  'link': 'http://www.calendario.com.br/feriados-nacionais/dia-de-finados.php',
  'name': 'Dia de Finados',
  'type': 'Feriado Nacional',
  'type_code': '1'},
 {'date': '15/11/2018',
  'description': 'A Proclamação da República foi um levante político-militar ocorrido em 15 de novembro de 1889 que instaurou a forma Republicana Federativa Presidencialista de governo no Brasil, derrubando a Monarquia e, por conseguinte, o imperador dom Pedro II.',
  'link': 'http://www.calendario.com.br/feriados-nacionais/proclamacao-da-republica.php',
  'name': 'Proclamação da República',
  'type': 'Feriado Nacional',
  'type_code': '1'},
 {'date': '20/11/2018',
  'description': 'Apesar de ser comemorado em todo o território nacional, conforme indica a Lei Federal nº 12.519, de 10 de novembro de 2011, o Dia Nacional de Zumbi e da Consciência Negra não é feriado. No entanto, alguns municípios decretam feriado municipal neste dia.',
  'link': 'http://www.calendario.com.br/feriados-nacionais/consciencia-negra.php',
  'name': 'Consciência Negra',
  'type': 'Dia Convencional',
  'type_code': '9'},
 {'date': '25/12/2018',
  'description': 'O Natal é comemorado anualmente em 25 de Dezembro. Originalmente destinado a celebrar o nascimento anual do Deus Sol no solstício de inverno, foi adaptado pela Igreja Católica no 3o século d.C., para permitir a conversão dos povos pagãos sob o domínio do Império Romano, passando a comemorar o nascimento de Jesus de Nazaré.',
  'link': 'http://www.calendario.com.br/feriados-nacionais/natal.php',
  'name': 'Natal',
  'type': 'Feriado Nacional',
  'type_code': '1'}]
