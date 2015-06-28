import re
import sublime
import sublime_plugin
from Default.paragraph import *
from . import jtextwrap as textwrap

class WrapLinesJustifiedCommand(WrapLinesCommand):
    ''' Same as parent, except using jtextwrap. '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, edit, width=0):
        if width == 0 and self.view.settings().get("wrap_width"):
            try:
                width = int(self.view.settings().get("wrap_width"))
            except TypeError:
                pass

        if width == 0 and self.view.settings().get("rulers"):
            # try and guess the wrap width from the ruler, if any
            try:
                width = int(self.view.settings().get("rulers")[0])
            except ValueError:
                pass
            except TypeError:
                pass

        if width == 0:
            width = 78

        # Make sure tabs are handled as per the current buffer
        tab_width = 8
        if self.view.settings().get("tab_size"):
            try:
                tab_width = int(self.view.settings().get("tab_size"))
            except TypeError:
                pass

        if tab_width == 0:
            tab_width == 8

        paragraphs = []
        for s in self.view.sel():
            paragraphs.extend(all_paragraphs_intersecting_selection(self.view, s))

        if len(paragraphs) > 0:
            self.view.sel().clear()
            for p in paragraphs:
                self.view.sel().add(p)

            # This isn't an ideal way to do it, as we loose the position of the
            # cursor within the paragraph: hence why the paragraph is selected
            # at the end.
            for s in self.view.sel():
                wrapper = textwrap.TextWrapper()
                wrapper.expand_tabs = False
                wrapper.width = width
                prefix = self.extract_prefix(s)
                if prefix:
                    wrapper.initial_indent = prefix
                    wrapper.subsequent_indent = prefix
                    wrapper.width -= self.width_in_spaces(prefix, tab_width)

                if wrapper.width < 0:
                    continue

                txt = self.view.substr(s)
                if prefix:
                    txt = txt.replace(prefix, u"")

                txt = txt.expandtabs(tab_width)

                txt = wrapper.fill(txt) + u"\n"
                self.view.replace(edit, s, txt)

            # It's unhelpful to have the entire paragraph selected, just leave the
            # selection at the end
            ends = [s.end() - 1 for s in self.view.sel()]
            self.view.sel().clear()
            for pt in ends:
                self.view.sel().add(sublime.Region(pt))
