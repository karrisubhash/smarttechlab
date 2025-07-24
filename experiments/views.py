
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
import matplotlib.pyplot as plt
import io

EXPERIMENTS = {
    "sieve-analysis": {
        "title": "Sieve Analysis – GFN",
        "slug": "sieve-analysis",
        "aim": "To determine the Grain Fineness Number of a given sand sample.",
        "procedure": [
            "Take 500g of sand.",
            "Put it through a series of sieves.",
            "Shake for 15 minutes.",
            "Weigh retained sand on each sieve.",
            "Calculate GFN using P×F method."
        ],
        "factors": [3, 10, 20, 40, 70, 140]
    }
}

def experiment_list(request):
    return render(request, 'experiments/experiment_list.html', {'experiments': EXPERIMENTS})


def run_experiment(request, slug):
    experiment = EXPERIMENTS.get(slug)
    if not experiment:
        return HttpResponse("Experiment not found", status=404)

    result = None
    steps = ""
    weights = []
    graph_data = {}
    weight_inputs = [""] * 6
    email = ""

    if request.method == "POST":
        email = request.POST.get("email", "")
        from_result = request.POST.get("from_result", "") == "true"

        try:
            weight_inputs = [request.POST.get(f'w{i}', "") for i in range(1, 7)]
            weights = [float(w) if w else 0.0 for w in weight_inputs]
            total_weight = sum(weights)

            if total_weight == 0:
                steps = "<span style='color:red;'>Total weight is zero. Please enter valid weights.</span>"
            else:
                factors = experiment["factors"]
                p_values = [(w / total_weight) * 100 for w in weights]
                pf_values = [round(p * f, 2) for p, f in zip(p_values, factors)]
                total_pf = round(sum(pf_values), 2)
                gfn = round(total_pf / 100, 2)
                result = gfn

                steps += "<strong>Formula:</strong><br>"
                steps += "P(%) = (Weight Retained / Total Weight) × 100<br>"
                steps += "P × F = P% × Sieve Factor<br><br>"
                steps += "<strong>Step-by-Step Calculations:</strong><br>"
                steps += f"Total Weight = {total_weight}g<br><br>"

                email_subject = "Sieve Analysis Result – GFN"
                email_html_message = """
                <h2>Observation Table</h2>
                <table border="1" cellpadding="6" cellspacing="0">
                    <tr><th>Sieve No.</th><th>Weight (g)</th><th>P (%)</th><th>P × F</th></tr>
                """

                for i in range(6):
                    w = weights[i]
                    f = factors[i]
                    p = round(p_values[i], 2)
                    pf = pf_values[i]
                    steps += f"Sieve No. {f}:<br>- Weight Retained = {w}g<br>- P(%) = {p}%<br>- P × F = {pf}<br><br>"
                    email_html_message += f"<tr><td>{f}</td><td>{w}</td><td>{p}</td><td>{pf}</td></tr>"

                steps += f"<strong>Σ(P × F) = {total_pf}</strong><br>"
                steps += f"<strong>GFN = Σ(P × F) / 100 = {total_pf} / 100 = <span style='color:green;'>{gfn}</span></strong><br>"

                email_html_message += "</table><br><h2>Calculation Explanation</h2>"
                email_html_message += f"<p>Total Weight = {total_weight}g</p>"

                for i in range(6):
                    w = weights[i]
                    f = factors[i]
                    p = round(p_values[i], 2)
                    pf = pf_values[i]
                    email_html_message += f"""
                    <p><strong>Sieve {f}:</strong><br>
                    Weight Retained = {w}g<br>
                    P(%) = ({w} / {total_weight}) × 100 = {p}%<br>
                    P × F = {p} × {f} = {pf}</p>
                    """

                email_html_message += f"""
                <p><strong>Σ(P × F) = {total_pf}</strong><br>
                <strong>GFN = {gfn}</strong></p>
                <h2>Graph:</h2>
                <img src="cid:graph_inline"><br><br>
                Regards,<br>Designed by Subhash
                """

                
                graph_data = {
                    'sieves': factors,
                    'percentages': [round(p, 2) for p in p_values]
                }

                buf = io.BytesIO()
                plt.figure(figsize=(6, 4))
                plt.plot(factors, graph_data['percentages'], marker='o', linestyle='-', color='blue')
                plt.xlabel('Sieve No.')
                plt.ylabel('P (%)')
                plt.title('Sieve Analysis Graph')
                plt.grid(True)
                plt.tight_layout()
                plt.savefig(buf, format='png')
                buf.seek(0)
                plt.close()

                
                if email and result and from_result:
                    msg = EmailMultiAlternatives(
                        subject=email_subject,
                        body="Please view this email in HTML mode.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[email],
                    )
                    msg.attach_alternative(email_html_message, "text/html")

                    image = MIMEImage(buf.read(), _subtype="png")
                    image.add_header('Content-ID', '<graph_inline>')
                    image.add_header("Content-Disposition", "inline", filename="graph.png")
                    msg.attach(image)

                    msg.send()
                    steps += f"<div class='alert alert-info mt-3'>Result sent to <strong>{email}</strong></div>"

        except Exception as e:
            steps = f"<span style='color:red;'>Error: {str(e)}</span>"

    return render(request, 'experiments/experiment_run.html', {
        'experiment': experiment,
        'weights': weights,
        'weight_inputs': weight_inputs,
        'result': result,
        'steps': steps,
        'graph_data': graph_data,
        'email': email,
    })
