# -*- coding: utf-8 -*-
import sys

ext = [
    {
        0: u'', 1: u'um', 2: u'dois', 3: u'três', 4: u'quatro', 5: u'cinco',
        6: u'seis', 7: u'sete', 8: u'oito', 9: u'nove', 10: u'dez',
        11: u'onze', 12: u'doze', 13: u'treze', 14: u'quatorze', 15: u'quinze',
        16: u'dezesseis', 17: u'dezessete', 18: u'dezoito', 19: u'dezenove'
    },
    {
        2: u'vinte', 3: u'trinta', 4: u'quarenta', 5: u'cinquenta',
        6: u'sessenta', 7: u'setenta', 8: u'oitenta', 9: u'noventa'
    },
    {
        1: u'cento', 2: u'duzentos', 3: u'trezentos',
        4: u'quatrocentos', 5: u'quinhentos', 6: u'seissentos',
        7: u'setessentos', 8: u'oitocentos', 9: u'novecentos'
    }
]

und = [
    u'', u' mil',
    (u' milhão', u' milhões'),
    (u' bilhão', u' bilhões'),
    (u' trilhão', u' trilhões')
]


def cent(s, grand):
    s = u'0' * (3 - len(s)) + s
    if s == u'000':
        return u''
    if s == u'100':
        return u'cem'
    ret = u''
    dez = s[1] + s[2]
    if s[0] != u'0':
        ret += ext[2][int(s[0])]
        if dez != u'00':
            ret += u' e '
    if int(dez) < 20:
        ret += ext[0][int(dez)]
    else:
        if s[1] != u'0':
            ret += ext[1][int(s[1])]
            if s[2] != u'0':
                ret += u' e ' + ext[0][int(s[2])]

    return ret + (type(und[grand]) == tuple and (int(s) > 1 and und[grand][1] or und[grand][0]) or und[grand])


def extenso(n):
    sn = str(int(n))
    ret = []
    grand = 0
    while sn:
        s = sn[-3:]
        sn = sn[:-3]
        ret.append(cent(s, grand))
        grand += 1
    ret.reverse()
    return u' e '.join([r for r in ret if r])


def numero_extenso(n, unidade=u'reais'):
    UNIDADE_NAMES = {
        u'reais': {
            u'plural': (u'reais', u'centavos'),
            u'singular': (u'real', u'centavo')
        },
        u'ha': {
            u'plural': (u'hectares', u'ares'),
            u'singular': (u'hectar', u'ar')
        },
    }
    sn = u'%.2f' % float(n)
    num, dec = sn.split(u'.')
    num_plural = int(num) != 1
    num_sufixo = UNIDADE_NAMES[unidade][num_plural and u'plural' or u'singular'][0]
    ret = u'%s %s' % (extenso(num), num_sufixo)
    if dec != u'00':
        dec_plural = int(dec) != 1
        dec_sufixo = UNIDADE_NAMES[unidade][dec_plural and u'plural' or u'singular'][1]
        ret += u' e %s %s' % (extenso(dec), dec_sufixo)
    return ret

# ctrl b para rodar os testes (no sublime)
if __name__ == '__main__':

    if len(sys.argv) >= 3:
        n = sys.argv[1]
        e = numero_extenso(n, sys.argv[2])
        print(n)
        print(e)

    elif len(sys.argv) == 2:
        n = sys.argv[1]
        e = numero_extenso(n)
        print(n)
        print(e)

    else:
        # testes
        for num in range(100, 150):
            for d in range(0, 100):
                n = u'%s.%s' % (num, d)
                print(n, u'\t', numero_extenso(n))
