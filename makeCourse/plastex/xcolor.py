#!/usr/bin/env python

"""
Partial support for `xcolor.sty` LaTeX Package.

Most features of xcolor are implemented, including color series and mixing.

Note that the following features are unimplemented:
    * Color blending (with \blendcolors)
    * Color masking (with \maskcolors)
    * Color testing (with \testcolors)
    * Localised color definitions (all colors are globally defined)
    * The tHsb color model and twheel function expressions

Current Issues:
    * Using \color to set the color of a block of content spanning multiple
      paragraphs does not work correctly.
"""

from plasTeX import Command, Environment, sourceChildren
from plasTeX.Packages.color import latex2htmlcolor
from enum import Enum
import re
import math

class Elements(Enum):
    empty = 0
    minus = 1
    plus = 2
    space = 3
    int = 4
    dec = 5
    id = 6
    model = 7
    symbol = 8
    comma = 9
    ext_id = 10
    dot = 11
    named = 12
    model_list = 13
    spec = 14
    spec_list = 15
    series_step = 16
    series_access = 17
    mix = 18
    mix_expr = 19
    func_expr = 20
    expr = 21

class ColorModel(Enum):
    natural = 0
    rgb = 1
    cmy = 2
    cmyk = 3
    hsb = 4
    gray = 5
    RGB = 6
    HSB = 7
    HTML = 8
    Gray = 9
    Hsb = 10
    wave = 11

class ColorError(Exception):
    pass

class ColorParser:
    tokens = None
    colors = {}
    target = ColorModel.natural
    current_color = None

    class ColorParserError(Exception):
        pass

    def empty(self):
        return {'element': Elements.empty, 'value': None}
    
    def int(self):
        if self.next['element'] == Elements.int:
            return self.tokens.pop(0)
        else:
            return None
    
    def num(self):
        if self.next['element'] == Elements.int and self.next['value'] >= 0:
            return self.tokens.pop(0)
        else:
            return None
    
    def dec(self):
        if self.next['element'] == Elements.dec or self.next['element'] == Elements.int:
            return self.tokens.pop(0)
        else:
            return None

    def div(self):
        if (self.next['element'] == Elements.dec or self.next['element'] == Elements.int) \
                and int(self.next['value']) != 0:
            return self.tokens.pop(0)
        else:
            return None

    def pct(self): 
        if (self.next['element'] == Elements.dec or self.next['element'] == Elements.int) \
                and self.next['value'] >=0 and self.next['value'] <=100:
            return self.tokens.pop(0)
        else:
            return None

    def id(self):
        if self.next['element'] == Elements.id:
            return self.tokens.pop(0)
        else:
            return None
    
    def function(self):
        if self.next['element'] == Elements.id:
            if self.next['value'] == 'wheel' or self.next['value'] == 'twheel':
                return self.tokens.pop(0)
        return None

    def dot(self):
        if self.next['element'] == Elements.symbol and self.next['value'] == '.':
            self.tokens.pop(0)
            return {'element': Elements.id, 'value': '.'}
        else:
            return None

    def named(self):
        if self.next['element'] == Elements.named:
            return self.tokens.pop(0)
        else:
            return None
    
    def ext_id(self):
        if self.next['element'] == Elements.id:
            id1 = self.tokens.pop(0)
            if self.next['element'] == Elements.symbol and self.next['value'] == '=':
                self.tokens.pop(0)
                id2 = self.tokens.pop(0)
                return {'element': Elements.ext_id, 'value': [id1['value'], id2['value']]}
            else:
                return {'element': Elements.ext_id, 'value': [id1['value'], id1['value']]}
        else:
            return None

    def id_list(self):
        ext_ids = [self.ext_id()]
        if ext_ids[0] is not None:
            while self.next['element'] == Elements.comma:
                self.tokens.pop(0)
                ext_ids.append(self.ext_id())
            return ext_ids
        else:
            return None

    def name(self):
        return self.id() or self.dot()
    
    def core_model(self):
        core_models = [ColorModel.rgb, ColorModel.cmy,
                ColorModel.cmyk, ColorModel.hsb, ColorModel.gray]
        if self.next['element'] == Elements.model and self.next['value'] in core_models: 
            return self.tokens.pop(0)
        else:
            return None
    
    def num_model(self):
        if self.next['element'] == Elements.model: 
            return self.tokens.pop(0)
        else:
            return None
        
    def model(self):
        return self.num_model() or self.named()

    def model_list_basic(self):
        models = [self.model()]
        if models[0] is not None:
            while self.next['element'] == Elements.symbol and self.next['value'] == '/':
                self.tokens.pop(0)
                models.append(self.model())
            return {'element': Elements.model_list, 'value': models}
        else:
            return None
    
    def model_list(self):
        first = self.model()
        if self.next['element'] == Elements.symbol and (self.next['value'] == ':' \
                or self.next['value'] == '/'):
            sep = self.tokens.pop(0)
            if sep['element'] == Elements.symbol and sep['value'] == ':':
                models = self.model_list_basic()
                models['core'] = first
                return models
            elif sep['element'] == Elements.symbol and sep['value'] == '/':
                models = self.model_list_basic()
                models['value'].insert(0, first)
                return models
            else:
                return None
        else:
            return {'element': Elements.model_list, 'value': [first]}

    def spec(self):
        if self.next['element'] == Elements.id:
            return self.tokens.pop(0)
        else:
            spec = [(self.int() or self.dec())['value']]
            valid_next = [Elements.int, Elements.dec, Elements.comma]
            if spec[0] is not None:
                while self.next['element'] in valid_next:
                    if self.next['element'] == Elements.comma:
                        self.tokens.pop(0)
                    spec.append((self.int() or self.dec())['value'])
                return {'element': Elements.spec, 'value': spec}
            else:
                return None

    def spec_list(self):
        specs = [self.spec()]
        if specs[0] is not None:
            while self.next['element'] == Elements.symbol and self.next['value'] == '/':
                self.tokens.pop(0)
                specs.append(self.spec())
            return {'element': Elements.spec_list, 'value': specs}
        else:
            return None

    def prefix(self):
        if self.next['element'] == Elements.minus:
            return self.tokens.pop(0)
        else:
            return None

    def postfix(self):
        if self.next['element'] == Elements.symbol and self.next['value'] == '!!':
            self.tokens.pop(0)
            if self.next['element'] == Elements.plus:
                plus = self.tokens.pop(0)
                return {'element': Elements.series_step, 'value': plus['value'] }
            else:
                obrace = self.tokens.pop(0) #[
                num = self.num()
                cbrace = self.tokens.pop(0) #]
                return {'element': Elements.series_access, 'value': num['value'] }
        return None

    def mix(self):
        if self.next['element'] == Elements.symbol and self.next['value'] == '!':
            self.tokens.pop(0)
            pct = self.pct()
            if self.next['element'] == Elements.symbol and self.next['value'] == '!':
                self.tokens.pop(0)
                name = self.name()
                return{'element': Elements.mix, 'pct': pct['value'], 'value': name['value'] }
            else:
                return{'element': Elements.mix, 'pct': pct['value'], 'value': 'white' }
        else:
            return None
    
    def mix_expr(self):
        mixes = [self.mix()]
        if mixes[0] is not None:
            while self.next['element'] == Elements.symbol and self.next['value'] == '!':
                mixes.append(self.mix())
            return {'element': Elements.mix_expr, 'value': mixes}
        else:
            return None

    def expr(self):
        prefix = self.prefix()
        name = self.name()
        mix = self.mix_expr()
        postfix = self.postfix()
        color = Color().makeColor('named',name['value'], self.colors, self.current_color).copy()

        if postfix is not None:
            if postfix['element'] == Elements.series_step:
                while postfix['value']>0:
                    self.colors[name['value']].series_step()
                    postfix['value'] -= 1
            elif postfix['element'] == Elements.series_access:
                color = self.colors[name['value']].series_n(postfix['value']).copy()

        if mix is not None:
            for m in mix['value']:
                mpct = m['pct']
                mcol = Color().makeColor('named',m['value'],
                        self.colors, self.current_color).as_model(color.model)
                color = color.mix(mcol, mpct)
            
        if prefix is not None and prefix['value']%2 == 1:
            color = color.complement
        
        return {'element': Elements.expr, 'value': color}
    
    def ext_expr(self):
        div = None
        model = self.core_model()
        if model is None: return None
        model = model['value']

        if self.next['element'] == Elements.comma:
            self.tokens.pop(0)
            div = self.div()
            div = div['value']
        
        if self.next['element'] == Elements.symbol and self.next['value'] == ':':
            self.tokens.pop(0)
            exprs = [self.expr()]
            if exprs[0] is None or self.next['element'] != Elements.comma: return None
            self.tokens.pop(0)
            decs = [self.dec()]
            if decs[0] is None: return None

            while self.next['element'] == Elements.symbol and self.next['value'] == ';':
                self.tokens.pop(0)
                exprs.append(self.expr())
                if exprs[-1] is None or self.next['element'] != Elements.comma: return None
                self.tokens.pop(0)
                decs.append(self.dec())
                if decs[-1] is None: return None

            if div is None:
                div = sum([d['value'] for d in decs])

            color = 0.0*(grayColor(0.).as_model(model))
            for expr,dec in zip(exprs,decs):
                color = color + (dec['value']/div)*(expr['value'].as_model(model))

            return {'element': Elements.expr, 'value': color.wrapped}
        else:
            return None
    
    def color(self):
        color_expr = self.ext_expr() or self.expr()
        if color_expr is None: return None
        color = color_expr['value']
        while self.next['element'] == Elements.symbol and self.next['value'] == '>':
            self.tokens.pop(0)
            func = self.function()
            args = []
            while self.next['element'] == Elements.comma:
                self.tokens.pop(0)
                arg = self.int()
                if arg is None:
                    raise ColorError("Invalid argument passed to color function.")
                args.append(arg['value'])

            if func['value'] == 'wheel':
                if len(args) == 0:
                    raise ColorError("Insufficient arguments for color function: wheel.")
                full_circle = 360. if len(args)<2 else args[1]
                angle = args[0]
                color = color.as_hsb
                color.h = (color.h + float(angle)/full_circle)
                color = color.wrapped
            else:
                raise ColorError("Color function {} is not implemented".format(func['value']))
        return color 

    @property
    def next(self):
        if len(self.tokens) > 0:
            return self.tokens[0]
        return self.empty()
    
    def parseColor(self, colorspec, model):
        if model is not None:
            self.scan(model)
            model_list = self.model_list()
            models = [m['value'] for m in model_list['value']]

            self.scan(colorspec)
            spec_list = self.spec_list()
            specs = [s['value'] for s in spec_list['value']]

            if self.target in models:
                color = Color().makeColor(self.target,
                        specs[models.index(self.target)], self.colors, self.current_color)
            else:
                color = Color().makeColor(models[0], specs[0], self.colors, self.current_color)
            
            core = model_list['core'] if 'core' in model_list else ColorModel.natural
            return color.as_model(core).as_model(self.target)
        else:
            self.scan(colorspec)
            color = self.color()
            return color
    
    def scan(self, expr):
        scanner = re.Scanner([
            (r',\s*', lambda s, t: {'element': Elements.comma, 'value': t}),
            (r'RGB|rgb|cmyk|cmy|HSB|hsb|Gray|gray|HTML|Hsb|tHsb|wave',
                lambda s, t: {'element': Elements.model, 'value': ColorModel[t]}),
            (r'named', lambda s, t: {'element': Elements.named, 'value': t}),
            (r'[-+]?(\d*\.\d+)|(\d+\.\d*)',
                lambda s, t: {'element': Elements.dec, 'value': float(t)}),
            (r'[-+]?\d+', lambda s, t: {'element': Elements.int, 'value': int(t)}),
            (r'-+', lambda s, t: {'element': Elements.minus, 'value': len(t)}),
            (r'\++', lambda s, t: {'element': Elements.plus, 'value': len(t)}),
            (r'\w+', lambda s, t: {'element': Elements.id, 'value': t}),
            (r'!!', lambda s, t: {'element': Elements.symbol, 'value': t}),
            (r'\s+', lambda s, t: None), 
            (r'.', lambda s, t: {'element': Elements.symbol, 'value': t}),
            ])
        self.tokens, unknown = scanner.scan(expr)
        return self.tokens

class Color:
    model = None
    
    def __repr__(self):
        return '<{}Color: {}>'.format(self.model, self.as_list)

    def mix(self, mix_color, p):
        mix_color = mix_color.as_model(self.model)
        c = [ a*(p/100.)+b*(1.-p/100.) for (a,b) in zip(self.as_list, mix_color.as_list)]
        return self.makeColor(self.model, c)
    
    def __add__(self, add_color):
        add_color = add_color.as_model(self.model)
        c = [ a+b for (a,b) in zip(self.as_list, add_color.as_list)]
        return self.makeColor(self.model, c)
    
    def __sub__(self, sub_color):
        sub_color = sub_color.as_model(self.model)
        c = [ a-b for (a,b) in zip(self.as_list, sub_color.as_list)]
        return self.makeColor(self.model, c)
    
    def __rmul__(self, dec ):
        c = [ dec*a for a in self.as_list ]
        return self.makeColor(self.model, c)

    def makeColor(self, model, spec, named={}, current_color=None):
        if spec == '.':
            return current_color
        if model == 'named':
            if spec in named:
                return named[spec]
            else:
                raise ColorError('Named color not found in color database.') 
        elif model == ColorModel.rgb:
            r,g,b = spec
            return rgbColor(r,g,b)
        elif model == ColorModel.RGB:
            r,g,b = spec
            return rgbColor(r/255.,g/255.,b/255.)
        elif model == ColorModel.cmyk:
            c,m,y,k = spec
            return cmykColor(c,m,y,k)
        elif model == ColorModel.cmy:
            c,m,y = spec
            return cmyColor(c,m,y)
        elif model == ColorModel.gray:
            return grayColor(spec[0])
        elif model == ColorModel.Gray:
            return grayColor(spec[0]/15.)
        elif model == ColorModel.hsb:
            h,s,b = spec
            return hsbColor(h,s,b)
        elif model == ColorModel.Hsb:
            h,s,b = spec
            return hsbColor(h/360.,s,b)
        elif model == ColorModel.HSB:
            h,s,b = spec
            return hsbColor(h/240.,s/240.,b/240.)
        elif model == ColorModel.wave:
            return waveColor(spec[0])
        else:
            raise ColorError('Unable to create requested ColorModel.')

    def as_model(self, model):
        if model == ColorModel.natural:
            return self
        if model == ColorModel.rgb:
            return self.as_rgb
        elif model == ColorModel.cmyk:
            return self.as_cmyk
        elif model == ColorModel.cmy:
            return self.as_cmy
        elif model == ColorModel.gray:
            return self.as_gray
        elif model == ColorModel.hsb:
            return self.as_hsb
        elif model == ColorModel.wave:
            return self.as_wave
        else:
            raise ColorError('Unable to convert to requested ColorModel.')
    
    def copy(self):
        c = [ a for a in self.as_list]
        return self.makeColor(self.model, c)
    
    @property
    def wrapped(self):
        c = [ a - math.floor(a) if a != 1. else a for a in self.as_list]
        return self.makeColor(self.model, c)

    @property
    def html(self):
        rgb = self.as_rgb
        return '#%.2X%.2X%.2X' % (min(int(rgb.r*255), 255),
                min(int(rgb.g*255), 255), min(int(rgb.b*255), 255))

class rgbColor(Color):
    model = ColorModel.rgb
    r = g = b = None

    def __init__(self, r, g, b):
        self.r, self.g, self.b = r, g, b

    @property
    def as_list(self):
        return [self.r, self.g, self.b]

    @property
    def as_rgb(self):
        return self
    
    @property
    def as_gray(self):
        return grayColor(0.3*self.r + 0.59*self.g + 0.11*self.b)
    
    @property
    def as_cmy(self):
        return cmyColor(1. - self.r, 1. - self.g, 1. - self.b)

    @property
    def as_hsb(self):
        maxc = max((self.r, self.g, self.b))
        minc = min((self.r, self.g, self.b))
        if minc == maxc:
            return hsbColor(0., 0., maxc)
        rc = (maxc-self.r) / (maxc-minc)
        gc = (maxc-self.g) / (maxc-minc)
        bc = (maxc-self.b) / (maxc-minc)
        if self.r == maxc:
            h = bc-gc
        elif self.g == maxc:
            h = 2.+rc-bc
        else:
            h = 4.+gc-rc
        h = (h/6.) % 1.
        return hsbColor(h, (maxc-minc) / maxc, maxc)
    
    @property
    def as_cmyk(self):
        (c,m,y) = (1.-self.r, 1.-self.g, 1.-self.b)
        k = min((c, m, y))
        ck = min(1., max(0., c - k))
        mk = min(1., max(0., m - k))
        yk = min(1., max(0., y - k))
        return cmykColor(ck,mk,yk,k)

    @property
    def complement(self):
        return rgbColor(1. - self.r, 1. - self.g, 1. - self.b)
    
class grayColor(Color):
    model = ColorModel.gray
    gray = None

    def __init__(self, gray):
        self.gray = gray
    
    @property
    def as_list(self):
        return [self.gray]
    
    @property
    def as_gray(self):
        return self

    @property
    def as_rgb(self):
        return rgbColor(self.gray,self.gray,self.gray)
    
    @property
    def as_cmy(self):
        return cmyColor(1.-self.gray, 1.-self.gray, 1.-self.gray)
    
    @property
    def as_cmyk(self):
        return cmykColor(0., 0., 0., 1.-self.gray)
    
    @property
    def as_hsb(self):
        return hsbColor(0., 0., 1.-self.gray)

    @property
    def complement(self):
        return grayColor(1. - self.gray)

class cmykColor(Color):
    model = ColorModel.cmyk
    c = m = y = k = None

    def __init__(self, c, m, y, k):
        self.c, self.m, self.y, self.k = c, m, y, k
    
    @property
    def as_list(self):
        return [self.c, self.m, self.y, self.k]
    
    @property
    def as_cmyk(self):
        return self
    
    @property
    def as_hsb(self):
        return self.as_rgb.as_hsb

    @property
    def as_cmy(self):
        c = min(1., self.c + self.k)
        m = min(1., self.m + self.k)
        y = min(1., self.y + self.k)
        return cmyColor(c, m, y)

    @property
    def as_gray(self):
        return grayColor(1. - min(1., 0.3*self.c + 0.59*self.m + 0.11*self.y + self.k))
    
    @property
    def as_rgb(self):
        return rgbColor((1-self.c)*(1-self.k), (1-self.m)*(1-self.k), (1-self.y)*(1-self.k))

    @property
    def complement(self):
        return self.as_cmy.complement.as_cmyk

class cmyColor(Color):
    model = ColorModel.cmy
    c = m = y = None

    def __init__(self, c, m, y):
        self.c, self.m, self.y = c, m, y
    
    @property
    def as_list(self):
        return [self.c, self.m, self.y]
    
    @property
    def as_cmy(self):
        return self
    
    @property
    def as_cmyk(self):
        k = min((self.c, self.m, self.y))
        ck = min(1., max(0., self.c - k))
        mk = min(1., max(0., self.m - k))
        yk = min(1., max(0., self.y - k))
        return cmykColor(ck,mk,yk,k)
    
    @property
    def as_rgb(self):
        return rgbColor(1.-self.c, 1.-self.m, 1.-self.y)
    
    @property
    def as_gray(self):
        gray = 1. - (0.3*self.c + 0.59*self.m + 0.11*self.y)
        return grayColor(gray)

    @property
    def as_hsb(self):
        return self.as_rgb.as_hsb
    
    @property
    def complement(self):
        return cmyColor(1.-self.c, 1.-self.m, 1.-self.y)

class hsbColor(Color):
    model = ColorModel.hsb
    h = s = b = None

    def __init__(self, h, s, b):
        self.h, self.s, self.b = h, s, b
    
    @property
    def as_list(self):
        return [self.h, self.s, self.b]
    
    @property
    def as_hsb(self):
        return self
    
    @property
    def as_cmyk(self):
        return self.as_rgb.as_cmyk
    
    @property
    def as_cmy(self):
        return self.as_rgb.as_cmy
    
    @property
    def as_rgb(self):
        if self.s == 0.: return (self.b, self.b, self.b)
        i = int(self.h*6.)
        f = (self.h*6.)-i
        p,q,t = self.b*(1.-self.s), self.b*(1.-self.s*f), self.b*(1.-self.s*(1.-f))
        i%=6
        if i == 0: return rgbColor(self.b, t, p)
        if i == 1: return rgbColor(q, self.b, p)
        if i == 2: return rgbColor(p, self.b, t)
        if i == 3: return rgbColor(p, q, self.b)
        if i == 4: return rgbColor(t, p, self.b)
        if i == 5: return rgbColor(self.b, p, q)
    
    @property
    def as_gray(self):
        return self.as_rgb.as_gray
    
    @property
    def complement(self):
        h = self.h+0.5 if self.h < 0.5 else self.h-0.5
        b = 1. - self.b*(1.-self.s)
        s = 0. if self.b == 0. else (self.b*self.s)/b
        return hsbColor(h,s,b)

class waveColor(Color):
    model = ColorModel.wave
    freq = None

    def __init__(self, freq):
        self.freq = freq
    
    @property
    def wrapped(self):
        return self

    @property
    def as_list(self):
        return [self.freq]
    
    def mix(self, mix_color, p):
        if (mix_color.model != ColorModel.wave):
            raise ColorError('Unable to mix non-wave color into to a wave color.')
        return waveColor(self.freq * (p/100.) + (1. - p/100.)*mix_color.freq)

    @property
    def as_wave(self):
        return self

    @property
    def as_rgb(self):
        return self.as_hsb.as_rgb

    @property
    def as_hsb(self):
        if self.freq<440:
            h = 1./6.*(4.+max(min((self.freq-440)/(380-440),1.),0.))
        elif self.freq < 490:
            h = 1./6.*(4.-max(min((self.freq-440)/(490-440),1.),0.))
        elif self.freq < 510:
            h = 1./6.*(2.+max(min((self.freq-510)/(490-510),1.),0.))
        elif self.freq < 580:
            h = 1./6.*(2.-max(min((self.freq-510)/(580-510),1.),0.))
        elif self.freq < 645:
            h = 1./6.*max(min((self.freq-645)/(580-645),1.),0.)
        else:
            h = 0.

        if self.freq < 420:
            b = 0.3+0.7*(self.freq-380)/(420-380)
        elif self.freq < 700:
            b = 1
        else:
            b = 0.3+0.7*(self.freq-780)/(700-780)
        return hsbColor(h,1.,max(min(b,1.),0.))

    @property
    def complement(self):
        raise ColorError('Unable to compute complement of wave color')

class ColorSeries(Color):
    step = []
    model = None
    method = None
    div = None
    base = None
    last = None
    current = None
    
    def __repr__(self):
        if self.method == 'last':
            return '<ColorSeries(model={},base={},last={})>'.format(self.model,
                    self.base, self.last)
        else:
            return '<ColorSeries(model={},base={},step={})>'.format(self.model,
                    self.base, self.step)

    def __init__(self, model, method, base, step = [], last = None):
        self.model = model
        self.method = method
        self.base = base.as_model(self.model)
        self.step = step
        self.last = last.as_model(self.model) if last is not None else None

    def reset(self,div):
        self.current = self.base
        
        if self.method == 'step':
            steplist = self.step
        elif self.method == 'grad':
            steplist = [a/div for a in self.step]
        elif self.method == 'last':
            steplist = [a/div for a in (self.last-self.base).as_list]
        else:
            raise ColorError('Unrecognised step method')

        self.step = self.makeColor(self.model, steplist)

    def series_step(self):
        self.current = self.current + self.step
        self.current = self.current.wrapped
    
    def series_n(self,n):
        color = self.base
        while n>0:
            color = color + self.step
            color = color.wrapped
            n += 1
        return color
    
    @property
    def as_list(self):
        return self.current.as_list
    
    @property
    def as_hsb(self):
        return self.current.as_hsb
    
    @property
    def as_cmyk(self):
        return self.current.as_cmyk
    
    @property
    def as_cmy(self):
        return self.current.as_cmy

    @property
    def as_rgb(self):
        return self.current.as_rgb
    
    @property
    def as_gray(self):
        return self.current.as_gray
    
    @property
    def complement(self):
        return self.current.complement

def dvipsnames():
    colors = {}
    colors['GreenYellow'] = cmykColor(0.15,0,0.69,0)
    colors['Yellow'] = cmykColor(0,0,1,0)
    colors['Goldenrod'] = cmykColor(0,0.10,0.84,0)
    colors['Dandelion'] = cmykColor(0,0.29,0.84,0)
    colors['Apricot'] = cmykColor(0,0.32,0.52,0)
    colors['Peach'] = cmykColor(0,0.50,0.70,0)
    colors['Melon'] = cmykColor(0,0.46,0.50,0)
    colors['YellowOrange'] = cmykColor(0,0.42,1,0)
    colors['Orange'] = cmykColor(0,0.61,0.87,0)
    colors['BurntOrange'] = cmykColor(0,0.51,1,0)
    colors['Bittersweet'] = cmykColor(0,0.75,1,0.24)
    colors['RedOrange'] = cmykColor(0,0.77,0.87,0)
    colors['Mahogany'] = cmykColor(0,0.85,0.87,0.35)
    colors['Maroon'] = cmykColor(0,0.87,0.68,0.32)
    colors['BrickRed'] = cmykColor(0,0.89,0.94,0.28)
    colors['Red'] = cmykColor(0,1,1,0)
    colors['OrangeRed'] = cmykColor(0,1,0.50,0)
    colors['RubineRed'] = cmykColor(0,1,0.13,0)
    colors['WildStrawberry'] = cmykColor(0,0.96,0.39,0)
    colors['Salmon'] = cmykColor(0,0.53,0.38,0)
    colors['CarnationPink'] = cmykColor(0,0.63,0,0)
    colors['Magenta'] = cmykColor(0,1,0,0)
    colors['VioletRed'] = cmykColor(0,0.81,0,0)
    colors['Rhodamine'] = cmykColor(0,0.82,0,0)
    colors['Mulberry'] = cmykColor(0.34,0.90,0,0.02)
    colors['RedViolet'] = cmykColor(0.07,0.90,0,0.34)
    colors['Fuchsia'] = cmykColor(0.47,0.91,0,0.08)
    colors['Lavender'] = cmykColor(0,0.48,0,0)
    colors['Thistle'] = cmykColor(0.12,0.59,0,0)
    colors['Orchid'] = cmykColor(0.32,0.64,0,0)
    colors['DarkOrchid'] = cmykColor(0.40,0.80,0.20,0)
    colors['Purple'] = cmykColor(0.45,0.86,0,0)
    colors['Plum'] = cmykColor(0.50,1,0,0)
    colors['Violet'] = cmykColor(0.79,0.88,0,0)
    colors['RoyalPurple'] = cmykColor(0.75,0.90,0,0)
    colors['BlueViolet'] = cmykColor(0.86,0.91,0,0.04)
    colors['Periwinkle'] = cmykColor(0.57,0.55,0,0)
    colors['CadetBlue'] = cmykColor(0.62,0.57,0.23,0)
    colors['CornflowerBlue'] = cmykColor(0.65,0.13,0,0)
    colors['MidnightBlue'] = cmykColor(0.98,0.13,0,0.43)
    colors['NavyBlue'] = cmykColor(0.94,0.54,0,0)
    colors['RoyalBlue'] = cmykColor(1,0.50,0,0)
    colors['Blue'] = cmykColor(1,1,0,0)
    colors['Cerulean'] = cmykColor(0.94,0.11,0,0)
    colors['Cyan'] = cmykColor(1,0,0,0)
    colors['ProcessBlue'] = cmykColor(0.96,0,0,0)
    colors['SkyBlue'] = cmykColor(0.62,0,0.12,0)
    colors['Turquoise'] = cmykColor(0.85,0,0.20,0)
    colors['TealBlue'] = cmykColor(0.86,0,0.34,0.02)
    colors['Aquamarine'] = cmykColor(0.82,0,0.30,0)
    colors['BlueGreen'] = cmykColor(0.85,0,0.33,0)
    colors['Emerald'] = cmykColor(1,0,0.50,0)
    colors['JungleGreen'] = cmykColor(0.99,0,0.52,0)
    colors['SeaGreen'] = cmykColor(0.69,0,0.50,0)
    colors['Green'] = cmykColor(1,0,1,0)
    colors['ForestGreen'] = cmykColor(0.91,0,0.88,0.12)
    colors['PineGreen'] = cmykColor(0.92,0,0.59,0.25)
    colors['LimeGreen'] = cmykColor(0.50,0,1,0)
    colors['YellowGreen'] = cmykColor(0.44,0,0.74,0)
    colors['SpringGreen'] = cmykColor(0.26,0,0.76,0)
    colors['OliveGreen'] = cmykColor(0.64,0,0.95,0.40)
    colors['RawSienna'] = cmykColor(0,0.72,1,0.45)
    colors['Sepia'] = cmykColor(0,0.83,1,0.70)
    colors['Brown'] = cmykColor(0,0.81,1,0.60)
    colors['Tan'] = cmykColor(0.14,0.42,0.56,0)
    colors['Gray'] = cmykColor(0,0,0,0.50)
    colors['Black'] = cmykColor(0,0,0,1)
    colors['White'] = cmykColor(0,0,0,0)
    return colors

def svgnames():
    colors = {}
    colors['AliceBlue'] = rgbColor(.94,.972,1)
    colors['AntiqueWhite'] = rgbColor(.98,.92,.844)
    colors['Aqua'] = rgbColor(0,1,1)
    colors['Aquamarine'] = rgbColor(.498,1,.83)
    colors['Azure'] = rgbColor(.94,1,1)
    colors['Beige'] = rgbColor(.96,.96,.864)
    colors['Bisque'] = rgbColor(1,.894,.77)
    colors['Black'] = rgbColor(0,0,0)
    colors['BlanchedAlmond'] = rgbColor(1,.92,.804)
    colors['Blue'] = rgbColor(0,0,1)
    colors['BlueViolet'] = rgbColor(.54,.17,.888)
    colors['Brown'] = rgbColor(.648,.165,.165)
    colors['BurlyWood'] = rgbColor(.87,.72,.53)
    colors['CadetBlue'] = rgbColor(.372,.62,.628)
    colors['Chartreuse'] = rgbColor(.498,1,0)
    colors['Chocolate'] = rgbColor(.824,.41,.116)
    colors['Coral'] = rgbColor(1,.498,.312)
    colors['CornflowerBlue'] = rgbColor(.392,.585,.93)
    colors['Cornsilk'] = rgbColor(1,.972,.864)
    colors['Crimson'] = rgbColor(.864,.08,.235)
    colors['Cyan'] = rgbColor(0,1,1)
    colors['DarkBlue'] = rgbColor(0,0,.545)
    colors['DarkCyan'] = rgbColor(0,.545,.545)
    colors['DarkGoldenrod'] = rgbColor(.72,.525,.044)
    colors['DarkGray'] = rgbColor(.664,.664,.664)
    colors['DarkGreen'] = rgbColor(0,.392,0)
    colors['DarkGrey'] = rgbColor(.664,.664,.664)
    colors['DarkKhaki'] = rgbColor(.74,.716,.42)
    colors['DarkMagenta'] = rgbColor(.545,0,.545)
    colors['DarkOliveGreen'] = rgbColor(.332,.42,.185)
    colors['DarkOrange'] = rgbColor(1,.55,0)
    colors['DarkOrchid'] = rgbColor(.6,.196,.8)
    colors['DarkRed'] = rgbColor(.545,0,0)
    colors['DarkSalmon'] = rgbColor(.912,.59,.48)
    colors['DarkSeaGreen'] = rgbColor(.56,.736,.56)
    colors['DarkSlateBlue'] = rgbColor(.284,.24,.545)
    colors['DarkSlateGray'] = rgbColor(.185,.31,.31)
    colors['DarkSlateGrey'] = rgbColor(.185,.31,.31)
    colors['DarkTurquoise'] = rgbColor(0,.808,.82)
    colors['DarkViolet'] = rgbColor(.58,0,.828)
    colors['DeepPink'] = rgbColor(1,.08,.576)
    colors['DeepSkyBlue'] = rgbColor(0,.75,1)
    colors['DimGray'] = rgbColor(.41,.41,.41)
    colors['DimGrey'] = rgbColor(.41,.41,.41)
    colors['DodgerBlue'] = rgbColor(.116,.565,1)
    colors['FireBrick'] = rgbColor(.698,.132,.132)
    colors['FloralWhite'] = rgbColor(1,.98,.94)
    colors['ForestGreen'] = rgbColor(.132,.545,.132)
    colors['Fuchsia'] = rgbColor(1,0,1)
    colors['Gainsboro'] = rgbColor(.864,.864,.864)
    colors['GhostWhite'] = rgbColor(.972,.972,1)
    colors['Gold'] = rgbColor(1,.844,0)
    colors['Goldenrod'] = rgbColor(.855,.648,.125)
    colors['Gray'] = rgbColor(.5,.5,.5)
    colors['Green'] = rgbColor(0,.5,0)
    colors['GreenYellow'] = rgbColor(.68,1,.185)
    colors['Grey'] = rgbColor(.5,.5,.5)
    colors['Honeydew'] = rgbColor(.94,1,.94)
    colors['HotPink'] = rgbColor(1,.41,.705)
    colors['IndianRed'] = rgbColor(.804,.36,.36)
    colors['Indigo'] = rgbColor(.294,0,.51)
    colors['Ivory'] = rgbColor(1,1,.94)
    colors['Khaki'] = rgbColor(.94,.9,.55)
    colors['Lavender'] = rgbColor(.9,.9,.98)
    colors['LavenderBlush'] = rgbColor(1,.94,.96)
    colors['LawnGreen'] = rgbColor(.488,.99,0)
    colors['LemonChiffon'] = rgbColor(1,.98,.804)
    colors['LightBlue'] = rgbColor(.68,.848,.9)
    colors['LightCoral'] = rgbColor(.94,.5,.5)
    colors['LightCyan'] = rgbColor(.88,1,1)
    colors['LightGoldenrod'] = rgbColor(.933,.867,.51)
    colors['LightGoldenrodYellow'] = rgbColor(.98,.98,.824)
    colors['LightGray'] = rgbColor(.828,.828,.828)
    colors['LightGreen'] = rgbColor(.565,.932,.565)
    colors['LightGrey'] = rgbColor(.828,.828,.828)
    colors['LightPink'] = rgbColor(1,.712,.756)
    colors['LightSalmon'] = rgbColor(1,.628,.48)
    colors['LightSeaGreen'] = rgbColor(.125,.698,.668)
    colors['LightSkyBlue'] = rgbColor(.53,.808,.98)
    colors['LightSlateBlue'] = rgbColor(.518,.44,1)
    colors['LightSlateGray'] = rgbColor(.468,.532,.6)
    colors['LightSlateGrey'] = rgbColor(.468,.532,.6)
    colors['LightSteelBlue'] = rgbColor(.69,.77,.87)
    colors['LightYellow'] = rgbColor(1,1,.88)
    colors['Lime'] = rgbColor(0,1,0)
    colors['LimeGreen'] = rgbColor(.196,.804,.196)
    colors['Linen'] = rgbColor(.98,.94,.9)
    colors['Magenta'] = rgbColor(1,0,1)
    colors['Maroon'] = rgbColor(.5,0,0)
    colors['MediumAquamarine'] = rgbColor(.4,.804,.668)
    colors['MediumBlue'] = rgbColor(0,0,.804)
    colors['MediumOrchid'] = rgbColor(.73,.332,.828)
    colors['MediumPurple'] = rgbColor(.576,.44,.86)
    colors['MediumSeaGreen'] = rgbColor(.235,.7,.444)
    colors['MediumSlateBlue'] = rgbColor(.484,.408,.932)
    colors['MediumSpringGreen'] = rgbColor(0,.98,.604)
    colors['MediumTurquoise'] = rgbColor(.284,.82,.8)
    colors['MediumVioletRed'] = rgbColor(.78,.084,.52)
    colors['MidnightBlue'] = rgbColor(.098,.098,.44)
    colors['MintCream'] = rgbColor(.96,1,.98)
    colors['MistyRose'] = rgbColor(1,.894,.884)
    colors['Moccasin'] = rgbColor(1,.894,.71)
    colors['NavajoWhite'] = rgbColor(1,.87,.68)
    colors['Navy'] = rgbColor(0,0,.5)
    colors['NavyBlue'] = rgbColor(0,0,.5)
    colors['OldLace'] = rgbColor(.992,.96,.9)
    colors['Olive'] = rgbColor(.5,.5,0)
    colors['OliveDrab'] = rgbColor(.42,.556,.136)
    colors['Orange'] = rgbColor(1,.648,0)
    colors['OrangeRed'] = rgbColor(1,.27,0)
    colors['Orchid'] = rgbColor(.855,.44,.84)
    colors['PaleGoldenrod'] = rgbColor(.932,.91,.668)
    colors['PaleGreen'] = rgbColor(.596,.985,.596)
    colors['PaleTurquoise'] = rgbColor(.688,.932,.932)
    colors['PaleVioletRed'] = rgbColor(.86,.44,.576)
    colors['PapayaWhip'] = rgbColor(1,.936,.835)
    colors['PeachPuff'] = rgbColor(1,.855,.725)
    colors['Peru'] = rgbColor(.804,.52,.248)
    colors['Pink'] = rgbColor(1,.752,.796)
    colors['Plum'] = rgbColor(.868,.628,.868)
    colors['PowderBlue'] = rgbColor(.69,.88,.9)
    colors['Purple'] = rgbColor(.5,0,.5)
    colors['Red'] = rgbColor(1,0,0)
    colors['RosyBrown'] = rgbColor(.736,.56,.56)
    colors['RoyalBlue'] = rgbColor(.255,.41,.884)
    colors['SaddleBrown'] = rgbColor(.545,.27,.075)
    colors['Salmon'] = rgbColor(.98,.5,.448)
    colors['SandyBrown'] = rgbColor(.956,.644,.376)
    colors['SeaGreen'] = rgbColor(.18,.545,.34)
    colors['Seashell'] = rgbColor(1,.96,.932)
    colors['Sienna'] = rgbColor(.628,.32,.176)
    colors['Silver'] = rgbColor(.752,.752,.752)
    colors['SkyBlue'] = rgbColor(.53,.808,.92)
    colors['SlateBlue'] = rgbColor(.415,.352,.804)
    colors['SlateGray'] = rgbColor(.44,.5,.565)
    colors['SlateGrey'] = rgbColor(.44,.5,.565)
    colors['Snow'] = rgbColor(1,.98,.98)
    colors['SpringGreen'] = rgbColor(0,1,.498)
    colors['SteelBlue'] = rgbColor(.275,.51,.705)
    colors['Tan'] = rgbColor(.824,.705,.55)
    colors['Teal'] = rgbColor(0,.5,.5)
    colors['Thistle'] = rgbColor(.848,.75,.848)
    colors['Tomato'] = rgbColor(1,.39,.28)
    colors['Turquoise'] = rgbColor(.25,.88,.815)
    colors['Violet'] = rgbColor(.932,.51,.932)
    colors['VioletRed'] = rgbColor(.816,.125,.565)
    colors['Wheat'] = rgbColor(.96,.87,.7)
    colors['White'] = rgbColor(1,1,1)
    colors['WhiteSmoke'] = rgbColor(.96,.96,.96)
    colors['Yellow'] = rgbColor(1,1,0)
    colors['YellowGreen'] = rgbColor(.604,.804,.196)
    return colors

def x11names():
    colors={}
    colors['AntiqueWhite1'] = rgbColor(1,.936,.86)
    colors['AntiqueWhite2'] = rgbColor(.932,.875,.8)
    colors['AntiqueWhite3'] = rgbColor(.804,.752,.69)
    colors['AntiqueWhite4'] = rgbColor(.545,.512,.47)
    colors['Aquamarine1'] = rgbColor(.498,1,.83)
    colors['Aquamarine2'] = rgbColor(.464,.932,.776)
    colors['Aquamarine3'] = rgbColor(.4,.804,.668)
    colors['Aquamarine4'] = rgbColor(.27,.545,.455)
    colors['Azure1'] = rgbColor(.94,1,1)
    colors['Azure2'] = rgbColor(.88,.932,.932)
    colors['Azure3'] = rgbColor(.756,.804,.804)
    colors['Azure4'] = rgbColor(.512,.545,.545)
    colors['Bisque1'] = rgbColor(1,.894,.77)
    colors['Bisque2'] = rgbColor(.932,.835,.716)
    colors['Bisque3'] = rgbColor(.804,.716,.62)
    colors['Bisque4'] = rgbColor(.545,.49,.42)
    colors['Blue1'] = rgbColor(0,0,1)
    colors['Blue2'] = rgbColor(0,0,.932)
    colors['Blue3'] = rgbColor(0,0,.804)
    colors['Blue4'] = rgbColor(0,0,.545)
    colors['Brown1'] = rgbColor(1,.25,.25)
    colors['Brown2'] = rgbColor(.932,.23,.23)
    colors['Brown3'] = rgbColor(.804,.2,.2)
    colors['Brown4'] = rgbColor(.545,.136,.136)
    colors['Burlywood1'] = rgbColor(1,.828,.608)
    colors['Burlywood2'] = rgbColor(.932,.772,.57)
    colors['Burlywood3'] = rgbColor(.804,.668,.49)
    colors['Burlywood4'] = rgbColor(.545,.45,.332)
    colors['CadetBlue1'] = rgbColor(.596,.96,1)
    colors['CadetBlue2'] = rgbColor(.556,.898,.932)
    colors['CadetBlue3'] = rgbColor(.48,.772,.804)
    colors['CadetBlue4'] = rgbColor(.325,.525,.545)
    colors['Chartreuse1'] = rgbColor(.498,1,0)
    colors['Chartreuse2'] = rgbColor(.464,.932,0)
    colors['Chartreuse3'] = rgbColor(.4,.804,0)
    colors['Chartreuse4'] = rgbColor(.27,.545,0)
    colors['Chocolate1'] = rgbColor(1,.498,.14)
    colors['Chocolate2'] = rgbColor(.932,.464,.13)
    colors['Chocolate3'] = rgbColor(.804,.4,.112)
    colors['Chocolate4'] = rgbColor(.545,.27,.075)
    colors['Coral1'] = rgbColor(1,.448,.336)
    colors['Coral2'] = rgbColor(.932,.415,.312)
    colors['Coral3'] = rgbColor(.804,.356,.27)
    colors['Coral4'] = rgbColor(.545,.244,.185)
    colors['Cornsilk1'] = rgbColor(1,.972,.864)
    colors['Cornsilk2'] = rgbColor(.932,.91,.804)
    colors['Cornsilk3'] = rgbColor(.804,.785,.694)
    colors['Cornsilk4'] = rgbColor(.545,.532,.47)
    colors['Cyan1'] = rgbColor(0,1,1)
    colors['Cyan2'] = rgbColor(0,.932,.932)
    colors['Cyan3'] = rgbColor(0,.804,.804)
    colors['Cyan4'] = rgbColor(0,.545,.545)
    colors['DarkGoldenrod1'] = rgbColor(1,.725,.06)
    colors['DarkGoldenrod2'] = rgbColor(.932,.68,.055)
    colors['DarkGoldenrod3'] = rgbColor(.804,.585,.048)
    colors['DarkGoldenrod4'] = rgbColor(.545,.396,.03)
    colors['DarkOliveGreen1'] = rgbColor(.792,1,.44)
    colors['DarkOliveGreen2'] = rgbColor(.736,.932,.408)
    colors['DarkOliveGreen3'] = rgbColor(.635,.804,.352)
    colors['DarkOliveGreen4'] = rgbColor(.43,.545,.24)
    colors['DarkOrange1'] = rgbColor(1,.498,0)
    colors['DarkOrange2'] = rgbColor(.932,.464,0)
    colors['DarkOrange3'] = rgbColor(.804,.4,0)
    colors['DarkOrange4'] = rgbColor(.545,.27,0)
    colors['DarkOrchid1'] = rgbColor(.75,.244,1)
    colors['DarkOrchid2'] = rgbColor(.698,.228,.932)
    colors['DarkOrchid3'] = rgbColor(.604,.196,.804)
    colors['DarkOrchid4'] = rgbColor(.408,.132,.545)
    colors['DarkSeaGreen1'] = rgbColor(.756,1,.756)
    colors['DarkSeaGreen2'] = rgbColor(.705,.932,.705)
    colors['DarkSeaGreen3'] = rgbColor(.608,.804,.608)
    colors['DarkSeaGreen4'] = rgbColor(.41,.545,.41)
    colors['DarkSlateGray1'] = rgbColor(.592,1,1)
    colors['DarkSlateGray2'] = rgbColor(.552,.932,.932)
    colors['DarkSlateGray3'] = rgbColor(.475,.804,.804)
    colors['DarkSlateGray4'] = rgbColor(.32,.545,.545)
    colors['DeepPink1'] = rgbColor(1,.08,.576)
    colors['DeepPink2'] = rgbColor(.932,.07,.536)
    colors['DeepPink3'] = rgbColor(.804,.064,.464)
    colors['DeepPink4'] = rgbColor(.545,.04,.312)
    colors['DeepSkyBlue1'] = rgbColor(0,.75,1)
    colors['DeepSkyBlue2'] = rgbColor(0,.698,.932)
    colors['DeepSkyBlue3'] = rgbColor(0,.604,.804)
    colors['DeepSkyBlue4'] = rgbColor(0,.408,.545)
    colors['DodgerBlue1'] = rgbColor(.116,.565,1)
    colors['DodgerBlue2'] = rgbColor(.11,.525,.932)
    colors['DodgerBlue3'] = rgbColor(.094,.455,.804)
    colors['DodgerBlue4'] = rgbColor(.064,.305,.545)
    colors['Firebrick1'] = rgbColor(1,.19,.19)
    colors['Firebrick2'] = rgbColor(.932,.172,.172)
    colors['Firebrick3'] = rgbColor(.804,.15,.15)
    colors['Firebrick4'] = rgbColor(.545,.1,.1)
    colors['Gold1'] = rgbColor(1,.844,0)
    colors['Gold2'] = rgbColor(.932,.79,0)
    colors['Gold3'] = rgbColor(.804,.68,0)
    colors['Gold4'] = rgbColor(.545,.46,0)
    colors['Goldenrod1'] = rgbColor(1,.756,.145)
    colors['Goldenrod2'] = rgbColor(.932,.705,.132)
    colors['Goldenrod3'] = rgbColor(.804,.608,.112)
    colors['Goldenrod4'] = rgbColor(.545,.41,.08)
    colors['Green1'] = rgbColor(0,1,0)
    colors['Green2'] = rgbColor(0,.932,0)
    colors['Green3'] = rgbColor(0,.804,0)
    colors['Green4'] = rgbColor(0,.545,0)
    colors['Honeydew1'] = rgbColor(.94,1,.94)
    colors['Honeydew2'] = rgbColor(.88,.932,.88)
    colors['Honeydew3'] = rgbColor(.756,.804,.756)
    colors['Honeydew4'] = rgbColor(.512,.545,.512)
    colors['HotPink1'] = rgbColor(1,.43,.705)
    colors['HotPink2'] = rgbColor(.932,.415,.655)
    colors['HotPink3'] = rgbColor(.804,.376,.565)
    colors['HotPink4'] = rgbColor(.545,.228,.385)
    colors['IndianRed1'] = rgbColor(1,.415,.415)
    colors['IndianRed2'] = rgbColor(.932,.39,.39)
    colors['IndianRed3'] = rgbColor(.804,.332,.332)
    colors['IndianRed4'] = rgbColor(.545,.228,.228)
    colors['Ivory1'] = rgbColor(1,1,.94)
    colors['Ivory2'] = rgbColor(.932,.932,.88)
    colors['Ivory3'] = rgbColor(.804,.804,.756)
    colors['Ivory4'] = rgbColor(.545,.545,.512)
    colors['Khaki1'] = rgbColor(1,.965,.56)
    colors['Khaki2'] = rgbColor(.932,.9,.52)
    colors['Khaki3'] = rgbColor(.804,.776,.45)
    colors['Khaki4'] = rgbColor(.545,.525,.305)
    colors['LavenderBlush1'] = rgbColor(1,.94,.96)
    colors['LavenderBlush2'] = rgbColor(.932,.88,.898)
    colors['LavenderBlush3'] = rgbColor(.804,.756,.772)
    colors['LavenderBlush4'] = rgbColor(.545,.512,.525)
    colors['LemonChiffon1'] = rgbColor(1,.98,.804)
    colors['LemonChiffon2'] = rgbColor(.932,.912,.75)
    colors['LemonChiffon3'] = rgbColor(.804,.79,.648)
    colors['LemonChiffon4'] = rgbColor(.545,.536,.44)
    colors['LightBlue1'] = rgbColor(.75,.936,1)
    colors['LightBlue2'] = rgbColor(.698,.875,.932)
    colors['LightBlue3'] = rgbColor(.604,.752,.804)
    colors['LightBlue4'] = rgbColor(.408,.512,.545)
    colors['LightCyan1'] = rgbColor(.88,1,1)
    colors['LightCyan2'] = rgbColor(.82,.932,.932)
    colors['LightCyan3'] = rgbColor(.705,.804,.804)
    colors['LightCyan4'] = rgbColor(.48,.545,.545)
    colors['LightGoldenrod1'] = rgbColor(1,.925,.545)
    colors['LightGoldenrod2'] = rgbColor(.932,.864,.51)
    colors['LightGoldenrod3'] = rgbColor(.804,.745,.44)
    colors['LightGoldenrod4'] = rgbColor(.545,.505,.298)
    colors['LightPink1'] = rgbColor(1,.684,.725)
    colors['LightPink2'] = rgbColor(.932,.635,.68)
    colors['LightPink3'] = rgbColor(.804,.55,.585)
    colors['LightPink4'] = rgbColor(.545,.372,.396)
    colors['LightSalmon1'] = rgbColor(1,.628,.48)
    colors['LightSalmon2'] = rgbColor(.932,.585,.448)
    colors['LightSalmon3'] = rgbColor(.804,.505,.385)
    colors['LightSalmon4'] = rgbColor(.545,.34,.26)
    colors['LightSkyBlue1'] = rgbColor(.69,.888,1)
    colors['LightSkyBlue2'] = rgbColor(.644,.828,.932)
    colors['LightSkyBlue3'] = rgbColor(.552,.712,.804)
    colors['LightSkyBlue4'] = rgbColor(.376,.484,.545)
    colors['LightSteelBlue1'] = rgbColor(.792,.884,1)
    colors['LightSteelBlue2'] = rgbColor(.736,.824,.932)
    colors['LightSteelBlue3'] = rgbColor(.635,.71,.804)
    colors['LightSteelBlue4'] = rgbColor(.43,.484,.545)
    colors['LightYellow1'] = rgbColor(1,1,.88)
    colors['LightYellow2'] = rgbColor(.932,.932,.82)
    colors['LightYellow3'] = rgbColor(.804,.804,.705)
    colors['LightYellow4'] = rgbColor(.545,.545,.48)
    colors['Magenta1'] = rgbColor(1,0,1)
    colors['Magenta2'] = rgbColor(.932,0,.932)
    colors['Magenta3'] = rgbColor(.804,0,.804)
    colors['Magenta4'] = rgbColor(.545,0,.545)
    colors['Maroon1'] = rgbColor(1,.204,.7)
    colors['Maroon2'] = rgbColor(.932,.19,.655)
    colors['Maroon3'] = rgbColor(.804,.16,.565)
    colors['Maroon4'] = rgbColor(.545,.11,.385)
    colors['MediumOrchid1'] = rgbColor(.88,.4,1)
    colors['MediumOrchid2'] = rgbColor(.82,.372,.932)
    colors['MediumOrchid3'] = rgbColor(.705,.32,.804)
    colors['MediumOrchid4'] = rgbColor(.48,.215,.545)
    colors['MediumPurple1'] = rgbColor(.67,.51,1)
    colors['MediumPurple2'] = rgbColor(.624,.475,.932)
    colors['MediumPurple3'] = rgbColor(.536,.408,.804)
    colors['MediumPurple4'] = rgbColor(.365,.28,.545)
    colors['MistyRose1'] = rgbColor(1,.894,.884)
    colors['MistyRose2'] = rgbColor(.932,.835,.824)
    colors['MistyRose3'] = rgbColor(.804,.716,.71)
    colors['MistyRose4'] = rgbColor(.545,.49,.484)
    colors['NavajoWhite1'] = rgbColor(1,.87,.68)
    colors['NavajoWhite2'] = rgbColor(.932,.81,.63)
    colors['NavajoWhite3'] = rgbColor(.804,.7,.545)
    colors['NavajoWhite4'] = rgbColor(.545,.475,.37)
    colors['OliveDrab1'] = rgbColor(.752,1,.244)
    colors['OliveDrab2'] = rgbColor(.7,.932,.228)
    colors['OliveDrab3'] = rgbColor(.604,.804,.196)
    colors['OliveDrab4'] = rgbColor(.41,.545,.132)
    colors['Orange1'] = rgbColor(1,.648,0)
    colors['Orange2'] = rgbColor(.932,.604,0)
    colors['Orange3'] = rgbColor(.804,.52,0)
    colors['Orange4'] = rgbColor(.545,.352,0)
    colors['OrangeRed1'] = rgbColor(1,.27,0)
    colors['OrangeRed2'] = rgbColor(.932,.25,0)
    colors['OrangeRed3'] = rgbColor(.804,.215,0)
    colors['OrangeRed4'] = rgbColor(.545,.145,0)
    colors['Orchid1'] = rgbColor(1,.512,.98)
    colors['Orchid2'] = rgbColor(.932,.48,.912)
    colors['Orchid3'] = rgbColor(.804,.41,.79)
    colors['Orchid4'] = rgbColor(.545,.28,.536)
    colors['PaleGreen1'] = rgbColor(.604,1,.604)
    colors['PaleGreen2'] = rgbColor(.565,.932,.565)
    colors['PaleGreen3'] = rgbColor(.488,.804,.488)
    colors['PaleGreen4'] = rgbColor(.33,.545,.33)
    colors['PaleTurquoise1'] = rgbColor(.732,1,1)
    colors['PaleTurquoise2'] = rgbColor(.684,.932,.932)
    colors['PaleTurquoise3'] = rgbColor(.59,.804,.804)
    colors['PaleTurquoise4'] = rgbColor(.4,.545,.545)
    colors['PaleVioletRed1'] = rgbColor(1,.51,.67)
    colors['PaleVioletRed2'] = rgbColor(.932,.475,.624)
    colors['PaleVioletRed3'] = rgbColor(.804,.408,.536)
    colors['PaleVioletRed4'] = rgbColor(.545,.28,.365)
    colors['PeachPuff1'] = rgbColor(1,.855,.725)
    colors['PeachPuff2'] = rgbColor(.932,.796,.68)
    colors['PeachPuff3'] = rgbColor(.804,.688,.585)
    colors['PeachPuff4'] = rgbColor(.545,.468,.396)
    colors['Pink1'] = rgbColor(1,.71,.772)
    colors['Pink2'] = rgbColor(.932,.664,.72)
    colors['Pink3'] = rgbColor(.804,.57,.62)
    colors['Pink4'] = rgbColor(.545,.39,.424)
    colors['Plum1'] = rgbColor(1,.732,1)
    colors['Plum2'] = rgbColor(.932,.684,.932)
    colors['Plum3'] = rgbColor(.804,.59,.804)
    colors['Plum4'] = rgbColor(.545,.4,.545)
    colors['Purple1'] = rgbColor(.608,.19,1)
    colors['Purple2'] = rgbColor(.57,.172,.932)
    colors['Purple3'] = rgbColor(.49,.15,.804)
    colors['Purple4'] = rgbColor(.332,.1,.545)
    colors['Red1'] = rgbColor(1,0,0)
    colors['Red2'] = rgbColor(.932,0,0)
    colors['Red3'] = rgbColor(.804,0,0)
    colors['Red4'] = rgbColor(.545,0,0)
    colors['RosyBrown1'] = rgbColor(1,.756,.756)
    colors['RosyBrown2'] = rgbColor(.932,.705,.705)
    colors['RosyBrown3'] = rgbColor(.804,.608,.608)
    colors['RosyBrown4'] = rgbColor(.545,.41,.41)
    colors['RoyalBlue1'] = rgbColor(.284,.464,1)
    colors['RoyalBlue2'] = rgbColor(.264,.43,.932)
    colors['RoyalBlue3'] = rgbColor(.228,.372,.804)
    colors['RoyalBlue4'] = rgbColor(.152,.25,.545)
    colors['Salmon1'] = rgbColor(1,.55,.41)
    colors['Salmon2'] = rgbColor(.932,.51,.385)
    colors['Salmon3'] = rgbColor(.804,.44,.33)
    colors['Salmon4'] = rgbColor(.545,.298,.224)
    colors['SeaGreen1'] = rgbColor(.33,1,.624)
    colors['SeaGreen2'] = rgbColor(.305,.932,.58)
    colors['SeaGreen3'] = rgbColor(.264,.804,.5)
    colors['SeaGreen4'] = rgbColor(.18,.545,.34)
    colors['Seashell1'] = rgbColor(1,.96,.932)
    colors['Seashell2'] = rgbColor(.932,.898,.87)
    colors['Seashell3'] = rgbColor(.804,.772,.75)
    colors['Seashell4'] = rgbColor(.545,.525,.51)
    colors['Sienna1'] = rgbColor(1,.51,.28)
    colors['Sienna2'] = rgbColor(.932,.475,.26)
    colors['Sienna3'] = rgbColor(.804,.408,.224)
    colors['Sienna4'] = rgbColor(.545,.28,.15)
    colors['SkyBlue1'] = rgbColor(.53,.808,1)
    colors['SkyBlue2'] = rgbColor(.494,.752,.932)
    colors['SkyBlue3'] = rgbColor(.424,.65,.804)
    colors['SkyBlue4'] = rgbColor(.29,.44,.545)
    colors['SlateBlue1'] = rgbColor(.512,.435,1)
    colors['SlateBlue2'] = rgbColor(.48,.404,.932)
    colors['SlateBlue3'] = rgbColor(.41,.35,.804)
    colors['SlateBlue4'] = rgbColor(.28,.235,.545)
    colors['SlateGray1'] = rgbColor(.776,.888,1)
    colors['SlateGray2'] = rgbColor(.725,.828,.932)
    colors['SlateGray3'] = rgbColor(.624,.712,.804)
    colors['SlateGray4'] = rgbColor(.424,.484,.545)
    colors['Snow1'] = rgbColor(1,.98,.98)
    colors['Snow2'] = rgbColor(.932,.912,.912)
    colors['Snow3'] = rgbColor(.804,.79,.79)
    colors['Snow4'] = rgbColor(.545,.536,.536)
    colors['SpringGreen1'] = rgbColor(0,1,.498)
    colors['SpringGreen2'] = rgbColor(0,.932,.464)
    colors['SpringGreen3'] = rgbColor(0,.804,.4)
    colors['SpringGreen4'] = rgbColor(0,.545,.27)
    colors['SteelBlue1'] = rgbColor(.39,.72,1)
    colors['SteelBlue2'] = rgbColor(.36,.675,.932)
    colors['SteelBlue3'] = rgbColor(.31,.58,.804)
    colors['SteelBlue4'] = rgbColor(.21,.392,.545)
    colors['Tan1'] = rgbColor(1,.648,.31)
    colors['Tan2'] = rgbColor(.932,.604,.288)
    colors['Tan3'] = rgbColor(.804,.52,.248)
    colors['Tan4'] = rgbColor(.545,.352,.17)
    colors['Thistle1'] = rgbColor(1,.884,1)
    colors['Thistle2'] = rgbColor(.932,.824,.932)
    colors['Thistle3'] = rgbColor(.804,.71,.804)
    colors['Thistle4'] = rgbColor(.545,.484,.545)
    colors['Tomato1'] = rgbColor(1,.39,.28)
    colors['Tomato2'] = rgbColor(.932,.36,.26)
    colors['Tomato3'] = rgbColor(.804,.31,.224)
    colors['Tomato4'] = rgbColor(.545,.21,.15)
    colors['Turquoise1'] = rgbColor(0,.96,1)
    colors['Turquoise2'] = rgbColor(0,.898,.932)
    colors['Turquoise3'] = rgbColor(0,.772,.804)
    colors['Turquoise4'] = rgbColor(0,.525,.545)
    colors['VioletRed1'] = rgbColor(1,.244,.59)
    colors['VioletRed2'] = rgbColor(.932,.228,.55)
    colors['VioletRed3'] = rgbColor(.804,.196,.47)
    colors['VioletRed4'] = rgbColor(.545,.132,.32)
    colors['Wheat1'] = rgbColor(1,.905,.73)
    colors['Wheat2'] = rgbColor(.932,.848,.684)
    colors['Wheat3'] = rgbColor(.804,.73,.59)
    colors['Wheat4'] = rgbColor(.545,.494,.4)
    colors['Yellow1'] = rgbColor(1,1,0)
    colors['Yellow2'] = rgbColor(.932,.932,0)
    colors['Yellow3'] = rgbColor(.804,.804,0)
    colors['Yellow4'] = rgbColor(.545,.545,0)
    colors['Gray0'] = rgbColor(.745,.745,.745)
    colors['Green0'] = rgbColor(0,1,0)
    colors['Grey0'] = rgbColor(.745,.745,.745)
    colors['Maroon0'] = rgbColor(.69,.19,.376)
    colors['Purple0'] = rgbColor(.628,.125,.94)
    return colors

def ProcessOptions(options, document):
    colors = {}
    target_model = ColorModel.natural
    if 'rgb' in options or 'RGB' in options:
        target_model = ColorModel.rgb
    if 'cmy' in options:
        target_model = ColorModel.cmy
    if 'cmyk' in options:
        target_model = ColorModel.cmyk
    if 'gray' in options or 'Gray' in options:
        target_model = ColorModel.gray
    
    document.userdata.setPath('packages/xcolor/target_model', target_model)
    document.userdata.setPath('packages/xcolor/colors', colors)
    document.userdata.setPath('packages/xcolor/colorseriescycle',16.)
    colors['red'] = rgbColor(1., 0., 0.).as_model(target_model)
    colors['green'] = rgbColor(0., 1., 0.).as_model(target_model)
    colors['blue'] = rgbColor(0., 0., 1.).as_model(target_model)
    colors['cyan'] = cmykColor(1., 0., 0., 0.).as_model(target_model)
    colors['magenta'] = cmykColor(0., 1., 0., 0.).as_model(target_model)
    colors['yellow'] = cmykColor(0., 0., 1., 0.).as_model(target_model)
    colors['black'] = grayColor(0.).as_model(target_model)
    colors['darkgray'] = grayColor(0.25).as_model(target_model)
    colors['gray'] = grayColor(0.5).as_model(target_model)
    colors['lightgray'] = grayColor(0.75).as_model(target_model)
    colors['white'] = grayColor(1.).as_model(target_model)
    colors['orange'] = rgbColor(1.,.5,0.).as_model(target_model)
    colors['violet'] = rgbColor(.5,0.,.5).as_model(target_model)
    colors['purple'] = rgbColor(.75,0.,.25).as_model(target_model)
    colors['brown'] = rgbColor(.75,.5,.25).as_model(target_model)
    colors['lime'] = rgbColor(.75,1.,0.).as_model(target_model)
    colors['pink'] = rgbColor(1.,.75,.75).as_model(target_model)
    colors['teal'] = rgbColor(0.,.5,.5).as_model(target_model)
    colors['olive'] = rgbColor(.5,.5,0.).as_model(target_model)

    if 'dvipsnames' in options:
        colors.update(dvipsnames())
    if 'svgnames' in options:
        colors.update(svgnames())
    if 'x11names' in options:
        colors.update(x11names())

class ColorCommandClass:
    parser = ColorParser()
    
    @property
    def current_color(self):
        node = self.parentNode
        while node is not None and not issubclass(node.__class__, ColorEnvironment):
            node = node.parentNode
        if node is not None:
            return node.parser.parseColor(node.attributes['color'], node.attributes['model'])
        else:
            return cmykColor(0., 0., 0., 1.)

class ColorEnvironment(Environment, ColorCommandClass):
    def invoke(self, tex):
        Environment.invoke(self, tex)
        u = self.ownerDocument.userdata
        self.parser.colors = u.getPath('packages/xcolor/colors')
        self.parser.target = u.getPath('packages/xcolor/target_model')

class ColorCommand(Command, ColorCommandClass):
    def invoke(self, tex):
        Command.invoke(self, tex)
        u = self.ownerDocument.userdata
        self.parser.colors = u.getPath('packages/xcolor/colors')
        self.parser.target = u.getPath('packages/xcolor/target_model')
    
class color(ColorEnvironment):
    args = '[ model:str ] color:str'

    def digest(self, tokens):
        res = Environment.digest(self, tokens)
        self.parser.current_color = self.current_color
        self.color = self.parser.parseColor(self.attributes['color'], self.attributes['model'])
        self.style['color'] = self.color.html
        return res

    @property
    def source(self):
        rgb = self.color.as_rgb
        return r'{{\color[rgb]{{{r:.15f},{g:.15f},{b:.15f}}}{children}}}'.format(r = rgb.r,
                g = rgb.g, b= rgb.b, children = sourceChildren(self))

class textcolor(ColorCommand):
    args = '[ model:str ] color:str self'

    def digest(self, tokens):
        res = Command.digest(self, tokens)
        self.parser.current_color = self.current_color
        self.color = self.parser.parseColor(self.attributes['color'], self.attributes['model'])
        self.style['color'] = self.color.html
        return res

class colorbox(ColorCommand):
    args = '[ model:str ] color:str self'

    def digest(self, tokens):
        res = Command.digest(self, tokens)
        self.parser.current_color = self.current_color
        self.color = self.parser.parseColor(self.attributes['color'], self.attributes['model'])
        self.style['background-color'] = self.color.html
        return res

class fcolorbox(ColorCommand):
    args = '[ f_model:str ] f_color:str [ bg_model:str] bg_color:str self'
    f_color = None

    def digest(self, tokens):
        res = Command.digest(self, tokens)
        a = self.attributes
        self.parser.current_color = self.current_color
        if a['bg_model'] is None:
            a['bg_model'] = a['f_model']
        self.f_color = self.parser.parseColor(a['f_color'], a['f_model'])
        self.color = self.parser.parseColor(a['bg_color'], a['bg_model'])
        self.style['background-color'] = self.color.html
        self.style['border'] = '1px solid %s' % self.f_color.html
        return res

# Color definition
class definecolor(ColorCommand):
    args = '[ type:str ] name:str model:str color:str'
    replace = True

    def digest(self, tokens):
        res = Command.digest(self, tokens)
        a = self.attributes
        self.parser.current_color = self.current_color
        if self.replace or a['name'] not in self.parser.colors:
            self.parser.colors[a['name']] = self.parser.parseColor(a['color'], a['model'])
    
    @property
    def source(self):
        return r'{children}'.format(children = sourceChildren(self))

class DefineNameColor(definecolor):
    args = 'type:str name:str model:str color:str'

class providecolor(definecolor):
    replace = False

class preparecolor(definecolor):
    pass

class colorlet(ColorCommand):
    args = '[ type:str ] name:str [ model:str ] color:str'

    def digest(self, tokens):
        res = Command.digest(self,tokens)
        a = self.attributes
        self.parser.current_color = self.current_color
        self.parser.colors[a['name']] = self.parser.parseColor(a['color'],'named')\
                .as_model(ColorModel[a['model']])
        return res

class definecolorset(ColorCommand):
    args = '[ type:str ] model:str head:str tail:str set_spec:str'
    replace = True
    def digest(self, tokens):
        res = Command.digest(self,tokens)
        a = self.attributes
        self.parser.current_color = self.current_color
        for s in a['set_spec'].split(';'):
            s = s.split(',')
            name = a['head'] + s[0] + a['tail']
            if self.replace or name not in self.parser.colors:
                self.parser.colors[name] = self.parser.parseColor(','.join(s[1:]), a['model'])
        return res

class providecolorset(definecolorset):
    replace = False

class preparecolorset(definecolorset):
    pass

class definecolors(ColorCommand):
    args = 'id_list:str'
    replace = True
    def digest(self, tokens):
        res = Command.digest(self,tokens)
        a = self.attributes
        self.parser.current_color = self.current_color
        self.parser.scan(a['id_list'])
        id_list = self.parser.id_list()
        for ids in id_list:
            src = self.parser.colors[ids['value'][1]]
            if self.replace or ids['value'][0] not in self.parser.colors:
                self.parser.colors[ids['value'][0]] = src.copy() 
            self.parser.colors[ids['value'][1]] = src
        return res

class providecolors(definecolors):
    replace = False

class colorseriescycle(Command):
    args = 'div:str'
    def invoke(self, tex):
        Command.invoke(self, tex)
        self.ownerDocument.userdata.setPath('packages/xcolor/colorseriescycle',float(a['div']))

class definecolorseries(ColorCommand):
    args = 'name:str model:str method:str [b_model:str] b_spec:str [s_model:str] s_spec:str'
    
    def digest(self, tokens):
        res = Command.digest(self,tokens)
        a = self.attributes
        self.parser.current_color = self.current_color
        self.parser.scan(a['model'])
        model = self.parser.core_model()
        model = model['value'] if 'value' in model else None
        base = self.parser.parseColor(a['b_spec'], self.attributes['b_model'])
        last = None
        step = None
        if a['method'] == 'last':
            last = self.parser.parseColor(a['s_spec'], self.attributes['s_model'])
            self.parser.colors[a['name']] = ColorSeries(model, a['method'], base, last = last)
        else:
            self.parser.scan(a['s_spec'])
            step = self.parser.spec()
            step =  step['value'] if 'value' in step else None
            self.parser.colors[a['name']] = ColorSeries(model, a['method'], base, step = step)
        return res

class resetcolorseries(Command):
    args = '[ div:str ] name:str'
    def invoke(self, tex):
        Command.invoke(self, tex)
        a = self.attributes
        u = self.ownerDocument.userdata
        colors = u.getPath('packages/xcolor/colors')
        if a['div'] is not None:
            div = float(a['div'])
        else:
            div = u.getPath('packages/xcolor/colorseriescycle')
        colors[a['name']].reset(div)

class pagecolor(Command):
    args = '[ model:str ] color:strV'

class nopagecolor(Command):
    pass
