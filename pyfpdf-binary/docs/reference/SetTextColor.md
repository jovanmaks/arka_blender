## SetTextColor ##

```python
fpdf.set_text_color(r: int, g: int = -1, b: int = -1)
```

### Description ###

Defines the color used for text. It can be expressed in RGB components or gray scale. The method can be called before the first page is created and the value is retained from page to page.

### Parameters ###

r:
> If `g` and `b` are given, red component; if not, indicates the gray level. Value between 0 and 255.

g:
> Green component (between 0 and 255).

b:
> Blue component (between 0 and 255).

### See also ###

[SetDrawColor](SetDrawColor.md), [SetFillColor](SetFillColor.md), [Text](Text.md), [Cell](Cell.md), [MultiCell](MultiCell.md).
