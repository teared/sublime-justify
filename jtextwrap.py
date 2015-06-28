import random
import re
import textwrap
from textwrap import dedent, indent

__all__ = ['TextWrapper', 'wrap', 'fill', 'shorten', 'dedent', 'indent']

class TextWrapper(textwrap.TextWrapper):
    '''Add justify functionality to TextWrapper.

    A new instance attributes controls the justification:
      justify (default: True)
        Toggles justification.

      random_spacing (default: True)
        If  True,  each  results can be different, but spacing distribution is
        more  uniform.  If  False,  a  new spaces always adding from the left.

      justify_last (default: 'left')
        Offers  four justification  options:  'left',  'right',  'center'  and
        'full'  justifying.  These variants specify  whether the last line  is
        flushed  left, flushed right, centered or fully justified (spread over
                                                      the whole column width).

      justify_indent (default: False)
        Enables spacing  between  text  and indent sequences.  Useful to avoid
        justification between  languages  comments  syntax  prefixes  and  the
        comments itself.

    '''
    def __init__(self, justify=True, random_spacing=True, justify_last='left', justify_indent=False, **kwargs):
        super().__init__(**kwargs)
        self.justify = justify
        self.random_spacing = random_spacing
        self.justify_last = justify_last
        self.justify_indent = justify_indent

    def _distribute(self, num, len):
        '''Distribute an integer over the list of desired length.
        Such as: 113 over length of 5 => [23, 23, 23, 22, 22]
        '''
        d = []
        for i in range(len):
            d.append(num // len)
        for i in range(num % len):
            d[i] += 1
        return d

    def _wrap_chunks(self, *args, **kwargs):
        ''' Wraps parent _wrap_chunks method, adding justifying. '''
        lines = super()._wrap_chunks(*args, **kwargs)

        if not self.justify:
            return lines

        if not lines:
            return []

        jlines = []
        for line in lines:
            chunks = self._split(line)
            nspaces = chunks.count(' ')

            # Avoid spacing after indent string.
            if not self.justify_indent:
                if self.initial_indent or self.subsequent_indent:
                    nspaces -= 1

            if nspaces == 0:
                jlines.append(line)
                continue

            jlen = self.width - len(line)
            add_spaces = self._distribute(jlen, nspaces)

            # Randomize spacing.
            if self.random_spacing:
                random.shuffle(add_spaces)

            # Avoid spacing after indent string.
            if not self.justify_indent:
                if self.initial_indent or self.subsequent_indent:
                    add_spaces.insert(0, 0)

            # Widen chunk spaces.
            for i, item in enumerate(chunks):
                if item != ' ':
                    continue
                factor = (add_spaces.pop(0) + 1)
                chunks[i] = ' ' * factor

            jlines.append(''.join(chunks))

        # Deal with the last line.
        last = {
            'left'   : lines[-1],
            'right'  : lines[-1].rjust(self.width),
            'center' : lines[-1].center(self.width).rstrip(),
            'full'   : jlines[-1]
        }
        jlines[-1] = last[self.justify_last]

        return jlines

    def wrap(self, text):
        ''' The same as parent function, except whitespace elimination. '''
        text = re.sub(' +', ' ', text.strip())
        return super().wrap(text)

    def fill(self, text):
        ''' The same as parent function, except whitespace elimination. '''
        text = re.sub(' +', ' ', text.strip())
        return super().fill(text)


# Same interface which textwrap module provides.
def wrap(text, width=70, **kwargs):
    ''' The same as textwrap.wrap() function. '''
    w = TextWrapper(width=width, **kwargs)
    return w.wrap(text)

def fill(text, width=70, **kwargs):
    ''' The same as textwrap.fill() function. '''
    w = TextWrapper(width=width, **kwargs)
    return w.fill(text)

def shorten(text, width, **kwargs):
    ''' The same as textwrap.shorten() function. '''
    w = TextWrapper(width=width, max_lines=1, **kwargs)
    return w.fill(' '.join(text.strip().split()))

if __name__ == '__main__':
    text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
    print(fill(text, justify_last='right', width=60))
