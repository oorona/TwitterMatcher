import matplotlib.lines as lines
import matplotlib.transforms as mtransforms
import matplotlib.text as mtext

class RankLine(lines.Line2D):
    def __init__(self, *args, **kwargs):
        self.text = mtext.Text(0, 0, '')
        lines.Line2D.__init__(self, *args, **kwargs)
        self.text.set_text(self.get_label())

    def set_figure(self, figure):
        self.text.set_figure(figure)
        lines.Line2D.set_figure(self, figure)

    def set_transform(self, transform):
        texttrans = transform + mtransforms.Affine2D().translate(2, -5)
        self.text.set_transform(texttrans)
        lines.Line2D.set_transform(self, transform)

    def set_data(self, x, y):
        if len(x):
            self.text.set_position((x[-1], y[-1]))
        lines.Line2D.set_data(self, x, y)

    def draw(self, renderer):        
        lines.Line2D.draw(self, renderer)
        self.text.draw(renderer)

