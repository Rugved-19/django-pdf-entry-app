# pdf_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.contrib import messages
from django.db.models import Sum
from django.template.loader import render_to_string

from .models import Entry, User
from .forms import EntryForm, UserForm

import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from weasyprint import HTML


def register_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login_page')
    else:
        form = UserForm()
    return render(request, 'register.html', {'form': form})


def login_page(request):
    users = User.objects.all()
    return render(request, 'login.html', {'users': users})


def user_page(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        raw_input = request.POST.get('raw_input')
        amount = request.POST.get('amount')

        try:
            amount = int(float(amount))  # Round decimal to nearest int
        except:
            amount = 0

        chunks = raw_input.split('.')
        decimal_count = len([chunk for chunk in chunks if chunk.strip() != ""])
        total = decimal_count * amount

        Entry.objects.create(user=user, raw_input=raw_input, amount=amount, total=total)
        return redirect('user_page', user_id=user.id)

    entries = Entry.objects.filter(user=user)
    return render(request, 'user_page.html', {'user': user, 'entries': entries})


def add_entry(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            raw_input = entry.raw_input
            chunks = raw_input.split('.')
            count = len([chunk for chunk in chunks if chunk.strip().isdigit()])
            entry.amount = count * int(request.POST.get('amount', 0))
            entry.user = user
            entry.save()
    return redirect('user_page', user_id=user.id)


def delete_entry(request, user_id, entry_id):
    entry = get_object_or_404(Entry, id=entry_id, user_id=user_id)
    entry.delete()
    return redirect('user_page', user_id=user_id)


def delete_all_entries(request, user_id):
    Entry.objects.filter(user_id=user_id).delete()
    return redirect('user_page', user_id=user_id)


def delete_all_entries_global(request):
    Entry.objects.all().delete()
    messages.success(request, "✅ All entries from all users have been deleted.")
    return redirect('login_page')


def delete_user(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        user.delete()
    return redirect('login_page')


def generate_pdf_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        entries = Entry.objects.filter(user=user)

        html_string = render_to_string('pdf_template.html', {
            'user': user,
            'entries': entries,
        })

        html = HTML(string=html_string)
        pdf_file = html.write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{user.name}_entries.pdf"'
        return response

    except User.DoesNotExist:
        return HttpResponse("User not found.", status=404)


def generate_pdf_all(request):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    width, height = letter
    y = height - 50

    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, y, "All User Entries")
    y -= 40

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Entry Data")
    p.drawString(300, y, "Amount")
    y -= 20
    p.setFont("Helvetica", 12)

    entries = Entry.objects.all()
    for entry in entries:
        if y < 50:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y, "Entry Data")
            p.drawString(300, y, "Amount")
            y -= 20
            p.setFont("Helvetica", 12)

        p.drawString(50, y, entry.raw_input)
        p.drawString(300, y, str(entry.amount))
        y -= 20

    p.save()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename='all_entries.pdf')
def generate_pdf_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        entries = Entry.objects.filter(user=user)

        # Calculate user's grand total
        grand_total = sum(entry.total for entry in entries)

        html_string = render_to_string('pdf_template.html', {
            'user': user,
            'entries': entries,
            'grand_total': grand_total,  # Pass to template
        })

        html = HTML(string=html_string)
        pdf_file = html.write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{user.name}_entries.pdf"'
        return response

    except User.DoesNotExist:
        return HttpResponse("User not found.", status=404)



def generate_combined_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="combined_entries.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    entries = Entry.objects.all().values_list('raw_input', 'amount', 'total')
    data = [['Entry Data', 'Amount', 'Total']] + list(entries)

    grand_total = sum(entry[2] for entry in entries)
    data.append(['', 'Grand Total:', grand_total])

    table = Table(data, colWidths=[200, 100, 100])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 16),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 14),
        ('BACKGROUND', (1, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (1, -1), (-1, -1), 'Helvetica-Bold'),
    ]))

    elements.append(table)
    doc.build(elements)

    return response
