import io
from django.db.models import Sum
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import legal
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from .serializers import IngredientsAmount


def download_recipe(values):
    '''Формирование pdf-списка покупок для скачивания.'''
    registerFont(TTFont(
        'Helvetica', 'data/fonts/Helvetica.ttf', 'Helvetica.ttf'))
    buffer = io.BytesIO()
    page = canvas.Canvas(buffer, pagesize=legal, bottomup=0)
    recipe_list = page.beginText()
    recipe_list.setTextOrigin(inch, inch)
    recipe_list.setFont('Helvetica', 14)
    lines = []
    for recipe in values:
        lines.append('===================')
        lines.append(recipe.title)
        lines.append('===================')
        lines.append(f'Время приготовления: {recipe.cooking_time} минут')
        lines.append(' ')
        ingredients_cart = (
            IngredientsAmount.objects.filter(recipe=recipe).values(
                'ingredient__title',
                'ingredient__measure_unit',
            ).order_by(
                'ingredient__title'
            ).annotate(ingredient_amount=Sum('amount'))
        )
        for number, ingredient in enumerate(ingredients_cart, start=1):
            lines.append(
                f"{number}. {ingredient['ingredient__title']}: "
                f"{ingredient['ingredient_amount']} "
                f"{ingredient['ingredient__measure_unit']}.",
            )
        lines.append(' ')
        lines.append(' ')

    for line in lines:
        recipe_list.textLine(line)

    page.drawText(recipe_list)
    page.showPage()
    page.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='recipe_list.pdf')
