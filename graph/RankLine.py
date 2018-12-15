import matplotlib.lines as lines
import matplotlib.transforms as mtransforms
import matplotlib.text as mtext

class RankLine(lines.Line2D):
    line = lines.Line2D([],[],color="black",linewidth=2)
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
        self.line.set_transform(transform)

    def set_data(self, x, y):
        if len(x):
            self.text.set_position((x[-1], y[-1]))
        lines.Line2D.set_data(self, x, y)

    def draw(self, renderer):        
        lines.Line2D.draw(self, renderer)
        i=0
        x,y =self.get_data()
        for yf in y :            
            if yf is not None:
                ydata=[yf-0.4,yf+0.4]
                break
            i+=1
 
        xdata=[x[i],x[i]]

        self.line.set_data(xdata,ydata)
        self.line.draw(renderer)
        self.text.draw(renderer)

